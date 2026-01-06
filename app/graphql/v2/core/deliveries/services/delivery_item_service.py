
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryItem

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_items_repository import (
    DeliveryItemsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import DeliveryItemInput


class DeliveryItemService:
    """Service for delivery item operations."""

    def __init__(
        self,
        repository: DeliveryItemsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, item_id: UUID) -> DeliveryItem:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundError(f"Delivery item with id {item_id} not found")
        return item

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryItem]:
        return await self.repository.list_by_delivery(delivery_id)

    async def create(self, input: DeliveryItemInput) -> DeliveryItem:
        return await self.repository.create(input.to_orm_model())

    async def update(self, item_id: UUID, input: DeliveryItemInput) -> DeliveryItem:
        if not await self.repository.exists(item_id):
            raise NotFoundError(f"Delivery item with id {item_id} not found")
        item = input.to_orm_model()
        item.id = item_id
        return await self.repository.update(item)

    async def delete(self, item_id: UUID) -> bool:
        if not await self.repository.exists(item_id):
            raise NotFoundError(f"Delivery item with id {item_id} not found")
        return await self.repository.delete(item_id)
