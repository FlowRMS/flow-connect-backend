from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryItemReceipt

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_item_receipts_repository import (
    DeliveryItemReceiptsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryItemReceiptInput


class DeliveryItemReceiptService:
    """Service for delivery item receipt operations."""

    def __init__(
        self,
        repository: DeliveryItemReceiptsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, receipt_id: UUID) -> DeliveryItemReceipt:
        receipt = await self.repository.get_by_id(receipt_id)
        if not receipt:
            raise NotFoundError(f"Delivery item receipt with id {receipt_id} not found")
        return receipt

    async def list_by_delivery_item(
        self, delivery_item_id: UUID
    ) -> list[DeliveryItemReceipt]:
        return await self.repository.list_by_delivery_item(delivery_item_id)

    async def create(self, input: DeliveryItemReceiptInput) -> DeliveryItemReceipt:
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, receipt_id: UUID, input: DeliveryItemReceiptInput
    ) -> DeliveryItemReceipt:
        if not await self.repository.exists(receipt_id):
            raise NotFoundError(f"Delivery item receipt with id {receipt_id} not found")
        receipt = input.to_orm_model()
        receipt.id = receipt_id
        return await self.repository.update(receipt)

    async def delete(self, receipt_id: UUID) -> bool:
        if not await self.repository.exists(receipt_id):
            raise NotFoundError(f"Delivery item receipt with id {receipt_id} not found")
        return await self.repository.delete(receipt_id)
