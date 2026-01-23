from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_issue_service import (
    DeliveryIssueService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_issue_response import (
    DeliveryIssueLiteResponse,
    DeliveryIssueResponse,
)


@strawberry.type
class DeliveryIssuesQueries:
    """GraphQL queries for DeliveryIssue entity."""

    @strawberry.field
    @inject
    async def delivery_issues(
        self,
        delivery_id: UUID,
        service: Injected[DeliveryIssueService],
    ) -> list[DeliveryIssueLiteResponse]:
        """List issues - returns lite response to avoid N+1 queries."""
        issues = await service.list_by_delivery(delivery_id)
        return DeliveryIssueLiteResponse.from_orm_model_list(issues)

    @strawberry.field
    @inject
    async def delivery_issue(
        self,
        id: UUID,
        service: Injected[DeliveryIssueService],
    ) -> DeliveryIssueResponse:
        issue = await service.get_by_id(id)
        return DeliveryIssueResponse.from_orm_model(issue)
