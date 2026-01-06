
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import Delivery

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.deliveries_repository import (
    DeliveriesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import DeliveryInput


class DeliveryService:
    """Service for delivery operations."""

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
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        delivery = input.to_orm_model()
        delivery.id = delivery_id
        return await self.repository.update(delivery)

    async def delete(self, delivery_id: UUID) -> bool:
        if not await self.repository.exists(delivery_id):
            raise NotFoundError(f"Delivery with id {delivery_id} not found")
        return await self.repository.delete(delivery_id)
