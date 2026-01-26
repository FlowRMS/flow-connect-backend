from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryItem
from sqlalchemy.orm import selectinload

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_items_repository import (
    DeliveryItemsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryItemInput


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
        existing = await self.repository.get_by_id(
            item_id,
            options=[
                selectinload(DeliveryItem.issues),
                selectinload(DeliveryItem.receipts),
            ],
        )
        if not existing:
            raise NotFoundError(f"Delivery item with id {item_id} not found")
        item = input.to_orm_model()
        item.id = item_id
        # Preserve child collections to avoid delete-orphan wipes on update.
        item.issues = existing.issues
        item.receipts = existing.receipts
        return await self.repository.update(item)

    async def delete(self, item_id: UUID) -> bool:
        if not await self.repository.exists(item_id):
            raise NotFoundError(f"Delivery item with id {item_id} not found")
        return await self.repository.delete(item_id)
