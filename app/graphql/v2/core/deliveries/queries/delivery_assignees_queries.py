from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_assignee_service import (
    DeliveryAssigneeService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_assignee_response import (
    DeliveryAssigneeLiteResponse,
    DeliveryAssigneeResponse,
)


@strawberry.type
class DeliveryAssigneesQueries:
    """GraphQL queries for DeliveryAssignee entity."""

    @strawberry.field
    @inject
    async def delivery_assignees(
        self,
        delivery_id: UUID,
        service: Injected[DeliveryAssigneeService],
    ) -> list[DeliveryAssigneeLiteResponse]:
        """List assignees - returns lite response to avoid N+1 queries."""
        assignees = await service.list_by_delivery(delivery_id)
        return DeliveryAssigneeLiteResponse.from_orm_model_list(assignees)

    @strawberry.field
    @inject
    async def delivery_assignee(
        self,
        id: UUID,
        service: Injected[DeliveryAssigneeService],
    ) -> DeliveryAssigneeResponse:
        assignee = await service.get_by_id(id)
        return DeliveryAssigneeResponse.from_orm_model(assignee)
