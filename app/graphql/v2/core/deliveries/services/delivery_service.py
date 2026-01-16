
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
        from datetime import datetime, timezone
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
        existing = await self.repository.get_with_relations(delivery_id)
        if not existing:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        delivery = input.to_orm_model()
        delivery.id = delivery_id
        should_sync_inventory = (
            existing.status != DeliveryStatus.RECEIVED
            and delivery.status == DeliveryStatus.RECEIVED
            and existing.inventory_synced_at is None
        )
        # Preserve child collections to avoid delete-orphan wipes on update.
        delivery.items = existing.items
        delivery.status_history = existing.status_history
        delivery.issues = existing.issues
        delivery.assignees = existing.assignees
        delivery.documents = existing.documents
        delivery.recurring_shipment = existing.recurring_shipment
        updated = await self.repository.update(delivery)
        if should_sync_inventory:
            _ = await self.inventory_sync_service.sync_received_delivery(updated.id)
        return updated

    async def delete(self, delivery_id: UUID) -> bool:
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return await self.repository.delete(delivery_id)
