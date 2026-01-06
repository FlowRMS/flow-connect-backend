
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryStatusHistory

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_status_history_repository import (
    DeliveryStatusHistoryRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import (
    DeliveryStatusHistoryInput,
)


class DeliveryStatusHistoryService:
    """Service for delivery status history operations."""

    def __init__(
        self,
        repository: DeliveryStatusHistoryRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, history_id: UUID) -> DeliveryStatusHistory:
        history = await self.repository.get_by_id(history_id)
        if not history:
            raise NotFoundError(
                f"Delivery status history with id {history_id} not found"
            )
        return history

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryStatusHistory]:
        return await self.repository.list_by_delivery(delivery_id)

    async def create(self, input: DeliveryStatusHistoryInput) -> DeliveryStatusHistory:
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, history_id: UUID, input: DeliveryStatusHistoryInput
    ) -> DeliveryStatusHistory:
        if not await self.repository.exists(history_id):
            raise NotFoundError(
                f"Delivery status history with id {history_id} not found"
            )
        history = input.to_orm_model()
        history.id = history_id
        return await self.repository.update(history)

    async def delete(self, history_id: UUID) -> bool:
        if not await self.repository.exists(history_id):
            raise NotFoundError(
                f"Delivery status history with id {history_id} not found"
            )
        return await self.repository.delete(history_id)
