
from datetime import date, datetime, timezone
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import Delivery
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.deliveries_repository import (
    DeliveriesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryInput
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
        return await self.repository.list_all(limit=limit, offset=offset)

    async def list_by_warehouse(self, warehouse_id: UUID, limit: int | None = None, offset: int | None = None) -> list[Delivery]:
        return await self.repository.list_by_warehouse(warehouse_id, limit=limit, offset=offset)

    async def create(self, input: DeliveryInput) -> Delivery:
        """
        Create a new delivery with automatic business logic:
        - Creates delivery in DRAFT status (unless specified otherwise)
        - Auto-creates initial status history entry
        - Sets created_by from auth context
        - If linked to recurring shipment, advances next_expected_date
        """
        from commons.db.v6 import RecurringShipment
        from commons.db.v6.warehouse.deliveries.delivery_status_history_model import (
            DeliveryStatusHistory,
        )
        from sqlalchemy import select

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

        # If linked to recurring shipment, advance next_expected_date to next occurrence
        if created_delivery.recurring_shipment_id:
            result = await self.repository.session.execute(
                select(RecurringShipment).where(
                    RecurringShipment.id == created_delivery.recurring_shipment_id
                )
            )
            recurring = result.scalar_one_or_none()
            if recurring and recurring.recurrence_pattern:
                # Calculate next date from the delivery's expected_date
                delivery_date = created_delivery.expected_date or date.today()
                next_date = calculate_next_date(recurring.recurrence_pattern, delivery_date)
                recurring.last_generated_date = delivery_date
                recurring.next_expected_date = next_date

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

        # Check if transitioning to RECEIVED status (before updating)
        is_being_received = (
            existing.status != DeliveryStatus.RECEIVED
            and input.status == DeliveryStatus(DeliveryStatus.RECEIVED.value)
        )

        should_sync_inventory = is_being_received and existing.inventory_synced_at is None
        should_generate_next = is_being_received and existing.recurring_shipment_id is not None

        # Update only scalar fields on existing entity (preserves relationships automatically)
        existing.po_number = input.po_number
        existing.warehouse_id = input.warehouse_id
        existing.vendor_id = input.vendor_id
        existing.carrier_id = input.carrier_id
        existing.tracking_number = input.tracking_number
        existing.status = DeliveryStatus(input.status.value)
        existing.expected_date = input.expected_date
        existing.arrived_at = input.arrived_at
        existing.receiving_started_at = input.receiving_started_at
        existing.received_at = input.received_at
        existing.origin_address_id = input.origin_address_id
        existing.destination_address_id = input.destination_address_id
        existing.recurring_shipment_id = input.recurring_shipment_id
        existing.vendor_contact_name = input.vendor_contact_name
        existing.vendor_contact_email = input.vendor_contact_email
        existing.notes = input.notes
        existing.updated_by_id = input.updated_by_id

        await self.repository.session.flush()

        # Sync inventory if needed
        if should_sync_inventory:
            _ = await self.inventory_sync_service.sync_received_delivery(existing.id)

        # Auto-generate next delivery from recurring shipment if needed
        recurring_id = existing.recurring_shipment_id
        if should_generate_next and recurring_id is not None:
            _ = await self._generate_next_recurring_delivery(recurring_id, delivery_id)

        return existing

    async def delete(self, delivery_id: UUID) -> bool:
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return await self.repository.delete(delivery_id)

    async def _generate_next_recurring_delivery(
        self, recurring_shipment_id: UUID, completed_delivery_id: UUID
    ) -> Delivery | None:
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
        from commons.db.v6.warehouse.deliveries.delivery_enums import (
            RecurringShipmentStatus,
            DeliveryItemStatus,
        )
        from commons.db.v6.warehouse.deliveries.delivery_item_model import DeliveryItem
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

        completed_delivery = await self.repository.session.get(Delivery, completed_delivery_id)
        if not completed_delivery:
            raise NotFoundError(f"Delivery with id {completed_delivery_id} not found")

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

        # Calculate next occurrence date based on the SCHEDULED date of the completed delivery.
        # We use expected_date (the scheduled delivery date) NOT received_at (when it was actually received)
        # because the recurrence pattern is based on the schedule, not actual receipt timing.
        # For example: if delivery was scheduled for Friday Jan 23 and received Monday Jan 19,
        # the next weekly Friday delivery should be Jan 30, not Jan 23 again.
        scheduled_date = completed_delivery.expected_date or date.today()
        next_date = calculate_next_date(recurring_shipment.recurrence_pattern, scheduled_date)

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
        )
        if self.auth_info and self.auth_info.flow_user_id:
            new_delivery.created_by_id = self.auth_info.flow_user_id  # type: ignore[assignment]

        self.repository.session.add(new_delivery)
        await self.repository.session.flush()

        # Create delivery items from recurring shipment's expected items
        pattern: dict = recurring_shipment.recurrence_pattern or {}
        expected_items: list[dict] = pattern.get("expectedItems", [])
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

        # Update recurring shipment: we've now generated `next_date`, so advance again.
        recurring_shipment.last_generated_date = next_date
        recurring_shipment.next_expected_date = calculate_next_date(
            recurring_shipment.recurrence_pattern, next_date
        )

        await self.repository.session.flush()

        return new_delivery
