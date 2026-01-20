
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_issue_service import (
    DeliveryIssueService,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryIssueInput
from app.graphql.v2.core.deliveries.strawberry.delivery_issue_response import (
    DeliveryIssueResponse,
)


@strawberry.type
class DeliveryIssuesMutations:
    """GraphQL mutations for DeliveryIssue entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_issue(
        self,
        input: DeliveryIssueInput,
        service: Injected[DeliveryIssueService],
    ) -> DeliveryIssueResponse:
        issue = await service.create(input)
        return DeliveryIssueResponse.from_orm_model(issue)

    @strawberry.mutation
    @inject
    async def update_delivery_issue(
        self,
        id: UUID,
        input: DeliveryIssueInput,
        service: Injected[DeliveryIssueService],
    ) -> DeliveryIssueResponse:
        issue = await service.update(id, input)
        return DeliveryIssueResponse.from_orm_model(issue)

    @strawberry.mutation
    @inject
    async def delete_delivery_issue(
        self,
        id: UUID,
        service: Injected[DeliveryIssueService],
    ) -> bool:
        return await service.delete(id)
