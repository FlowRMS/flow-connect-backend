
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryAssignee

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_assignees_repository import (
    DeliveryAssigneesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryAssigneeInput


class DeliveryAssigneeService:
    """Service for delivery assignee operations."""

    def __init__(
        self,
        repository: DeliveryAssigneesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, assignee_id: UUID) -> DeliveryAssignee:
        assignee = await self.repository.get_by_id(assignee_id)
        if not assignee:
            raise NotFoundError(
                f"Delivery assignee with id {assignee_id} not found"
            )
        return assignee

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryAssignee]:
        return await self.repository.list_by_delivery(delivery_id)

    async def create(self, input: DeliveryAssigneeInput) -> DeliveryAssignee:
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, assignee_id: UUID, input: DeliveryAssigneeInput
    ) -> DeliveryAssignee:
        if not await self.repository.exists(assignee_id):
            raise NotFoundError(
                f"Delivery assignee with id {assignee_id} not found"
            )
        assignee = input.to_orm_model()
        assignee.id = assignee_id
        return await self.repository.update(assignee)

    async def delete(self, assignee_id: UUID) -> bool:
        if not await self.repository.exists(assignee_id):
            raise NotFoundError(
                f"Delivery assignee with id {assignee_id} not found"
            )
        return await self.repository.delete(assignee_id)
