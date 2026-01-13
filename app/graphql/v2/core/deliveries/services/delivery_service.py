
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import Delivery

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.deliveries_repository import (
    DeliveriesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import DeliveryInput


class DeliveryService:

    def __init__(
        self,
        repository: DeliveriesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, delivery_id: UUID) -> Delivery:
        delivery = await self.repository.get_with_relations(delivery_id)
        if not delivery:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return delivery

    async def list_all(self) -> list[Delivery]:
        return await self.repository.list_all_with_relations()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[Delivery]:
        return await self.repository.list_by_warehouse(warehouse_id)

    async def create(self, input: DeliveryInput) -> Delivery:
        return await self.repository.create(input.to_orm_model())

    async def update(self, delivery_id: UUID, input: DeliveryInput) -> Delivery:
        existing = await self.repository.get_with_relations(delivery_id)
        if not existing:
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        delivery = input.to_orm_model()
        delivery.id = delivery_id
        # Preserve child collections to avoid delete-orphan wipes on update.
        delivery.items = existing.items
        delivery.status_history = existing.status_history
        delivery.issues = existing.issues
        delivery.assignees = existing.assignees
        delivery.documents = existing.documents
        delivery.recurring_shipment = existing.recurring_shipment
        return await self.repository.update(delivery)

    async def delete(self, delivery_id: UUID) -> bool:
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return await self.repository.delete(delivery_id)
