
from datetime import date, datetime, timezone
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import Delivery
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.deliveries_repository import (
    DeliveriesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import DeliveryInput
from app.graphql.v2.core.deliveries.services.delivery_inventory_sync_service import (
    DeliveryInventorySyncService,
)
from app.graphql.v2.core.deliveries.utils.recurrence_utils import calculate_next_date


class DeliveryService:

    def __init__(
        self,
        repository: DeliveriesRepository,
        auth_info: AuthInfo,
        inventory_sync_service: DeliveryInventorySyncService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info
        self.inventory_sync_service = inventory_sync_service

    async def get_by_id(self, delivery_id: UUID) -> Delivery:
        delivery = await self.repository.get_with_relations(delivery_id)
        if not delivery:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return delivery

    async def list_all(self, limit: int | None = None, offset: int | None = None) -> list[Delivery]:
        return await self.repository.list_all_with_relations(limit=limit, offset=offset)

    async def list_by_warehouse(self, warehouse_id: UUID, limit: int | None = None, offset: int | None = None) -> list[Delivery]:
        return await self.repository.list_by_warehouse(warehouse_id, limit=limit, offset=offset)

    async def create(self, input: DeliveryInput) -> Delivery:
        """
        Create a new delivery with automatic business logic:
        - Creates delivery in DRAFT status (unless specified otherwise)
        - Auto-creates initial status history entry
        - Sets created_by from auth context
        """
        from commons.db.v6.warehouse.deliveries.delivery_status_history_model import (
            DeliveryStatusHistory,
        )

        # Create delivery model from input
        delivery = input.to_orm_model()

        # Ensure delivery starts in DRAFT if not specified
        if not delivery.status:
            delivery.status = DeliveryStatus.DRAFT

        # Create delivery first to get delivery_id for status history
        created_delivery = await self.repository.create(delivery)

        # Auto-create initial status history after delivery exists
        initial_status_history = DeliveryStatusHistory(
            delivery_id=created_delivery.id,
            status=delivery.status,
            timestamp=datetime.now(timezone.utc),
            user_id=self.auth_info.flow_user_id if self.auth_info else None,
            note=f"Delivery created in {delivery.status.value} status",
        )
        self.repository.session.add(initial_status_history)
        await self.repository.session.flush()

        return created_delivery

    async def update(self, delivery_id: UUID, input: DeliveryInput) -> Delivery:
        """
        Update delivery with automatic business logic:
        - Syncs inventory when marked as RECEIVED
        - Auto-generates next delivery from recurring shipment (if applicable)
        - Updates recurring shipment's next_expected_date
        """
        existing = await self.repository.get_with_relations(delivery_id)
        if not existing:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")

        delivery = input.to_orm_model()
        delivery.id = delivery_id

        # Check if transitioning to RECEIVED status
        is_being_received = (
            existing.status != DeliveryStatus.RECEIVED
            and delivery.status == DeliveryStatus.RECEIVED
        )

        should_sync_inventory = is_being_received and existing.inventory_synced_at is None
        should_generate_next = is_being_received and existing.recurring_shipment_id is not None

        # Preserve child collections to avoid delete-orphan wipes on update.
        delivery.items = existing.items
        delivery.status_history = existing.status_history
        delivery.issues = existing.issues
        delivery.assignees = existing.assignees
        delivery.documents = existing.documents
        delivery.recurring_shipment = existing.recurring_shipment

        updated = await self.repository.update(delivery)

        # Sync inventory if needed
        if should_sync_inventory:
            _ = await self.inventory_sync_service.sync_received_delivery(updated.id)

        # Auto-generate next delivery from recurring shipment if needed
        if should_generate_next:
            await self._generate_next_recurring_delivery(existing.recurring_shipment_id, delivery_id)

        return updated

    async def delete(self, delivery_id: UUID) -> bool:
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return await self.repository.delete(delivery_id)

    async def _generate_next_recurring_delivery(
        self, recurring_shipment_id: UUID, completed_delivery_id: UUID
    ) -> Delivery:
        """
        Auto-generate the next delivery from a recurring shipment.

        This is called when a delivery is marked as RECEIVED.

        Steps:
        1. Fetch the recurring shipment
        2. Calculate next occurrence date using recurrence pattern
        3. Create new delivery with expected items
        4. Create delivery items from recurring shipment's expected items
        5. Update recurring shipment's last_generated_date and next_expected_date

        Args:
            recurring_shipment_id: ID of the recurring shipment
            completed_delivery_id: ID of the delivery that was just completed

        Returns:
            The newly created delivery

        Raises:
            NotFoundError: If recurring shipment not found
        """
        from commons.db.v6 import RecurringShipment
        from commons.db.v6.warehouse.deliveries.delivery_enums import RecurringShipmentStatus
        from commons.db.v6.warehouse.deliveries.delivery_item_model import DeliveryItem
        from commons.db.v6.warehouse.deliveries.delivery_item_enums import DeliveryItemStatus
        from commons.db.v6.warehouse.deliveries.delivery_status_history_model import (
            DeliveryStatusHistory,
        )
        from sqlalchemy import select

        # Fetch recurring shipment
        result = await self.repository.session.execute(
            select(RecurringShipment).where(RecurringShipment.id == recurring_shipment_id)
        )
        recurring_shipment = result.scalar_one_or_none()

        if not recurring_shipment:
            raise NotFoundError(f"Recurring shipment with id {recurring_shipment_id} not found")

        # Check if recurring shipment is still active
        if recurring_shipment.status != RecurringShipmentStatus.ACTIVE:
            # Don't generate next delivery if shipment is paused or cancelled
            return None

        # Check if we've reached the end date
        if recurring_shipment.end_date and date.today() >= recurring_shipment.end_date:
            # Mark recurring shipment as completed
            recurring_shipment.status = RecurringShipmentStatus.CANCELLED
            await self.repository.session.flush()
            return None

        # Calculate next occurrence date
        current_date = recurring_shipment.next_expected_date or date.today()
        next_date = calculate_next_date(recurring_shipment.recurrence_pattern, current_date)

        # Generate PO number (simple auto-increment based on year)
        year = next_date.year
        po_number = f"PO-{year}-{str(hash(str(recurring_shipment.id) + str(next_date)))[-6:]}"

        # Create new delivery
        new_delivery = Delivery(
            po_number=po_number,
            warehouse_id=recurring_shipment.warehouse_id,
            vendor_id=recurring_shipment.vendor_id,
            carrier_id=None,
            tracking_number=None,
            status=DeliveryStatus.PENDING,
            expected_date=next_date,
            recurring_shipment_id=recurring_shipment.id,
            vendor_contact_name=recurring_shipment.vendor_contact_name,
            vendor_contact_email=recurring_shipment.vendor_contact_email,
            notes=f"Auto-generated from recurring shipment: {recurring_shipment.name}",
            created_by_id=self.auth_info.flow_user_id if self.auth_info else None,
        )

        self.repository.session.add(new_delivery)
        await self.repository.session.flush()

        # Create delivery items from recurring shipment's expected items
        expected_items = recurring_shipment.recurrence_pattern.get("expectedItems", [])
        for item in expected_items:
            delivery_item = DeliveryItem(
                delivery_id=new_delivery.id,
                product_id=UUID(item["productId"]),
                expected_quantity=item.get("expectedQuantity", 0),
                received_quantity=0,
                damaged_quantity=0,
                status=DeliveryItemStatus.PENDING,
            )
            self.repository.session.add(delivery_item)

        # Create initial status history
        status_history = DeliveryStatusHistory(
            delivery_id=new_delivery.id,
            status=DeliveryStatus.PENDING,
            timestamp=datetime.now(timezone.utc),
            user_id=self.auth_info.flow_user_id if self.auth_info else None,
            note=f"Auto-generated from recurring shipment (after completing {completed_delivery_id})",
        )
        self.repository.session.add(status_history)

        # Update recurring shipment
        recurring_shipment.last_generated_date = date.today()
        recurring_shipment.next_expected_date = next_date

        await self.repository.session.flush()

        return new_delivery
