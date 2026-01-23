from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryIssue

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_issues_repository import (
    DeliveryIssuesRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryIssueInput


class DeliveryIssueService:
    """Service for delivery issue operations."""

    def __init__(
        self,
        repository: DeliveryIssuesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, issue_id: UUID) -> DeliveryIssue:
        issue = await self.repository.get_by_id(issue_id)
        if not issue:
            raise NotFoundError(f"Delivery issue with id {issue_id} not found")
        return issue

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryIssue]:
        return await self.repository.list_by_delivery(delivery_id)

    async def create(self, input: DeliveryIssueInput) -> DeliveryIssue:
        return await self.repository.create(input.to_orm_model())

    async def update(self, issue_id: UUID, input: DeliveryIssueInput) -> DeliveryIssue:
        if not await self.repository.exists(issue_id):
            raise NotFoundError(f"Delivery issue with id {issue_id} not found")
        issue = input.to_orm_model()
        issue.id = issue_id
        return await self.repository.update(issue)

    async def delete(self, issue_id: UUID) -> bool:
        if not await self.repository.exists(issue_id):
            raise NotFoundError(f"Delivery issue with id {issue_id} not found")
        return await self.repository.delete(issue_id)
