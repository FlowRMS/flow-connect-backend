from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_assignee_service import (
    DeliveryAssigneeService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_assignee_response import (
    DeliveryAssigneeResponse,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryAssigneeInput


@strawberry.type
class DeliveryAssigneesMutations:
    """GraphQL mutations for DeliveryAssignee entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_assignee(
        self,
        input: DeliveryAssigneeInput,
        service: Injected[DeliveryAssigneeService],
    ) -> DeliveryAssigneeResponse:
        assignee = await service.create(input)
        return DeliveryAssigneeResponse.from_orm_model(assignee)

    @strawberry.mutation
    @inject
    async def update_delivery_assignee(
        self,
        id: UUID,
        input: DeliveryAssigneeInput,
        service: Injected[DeliveryAssigneeService],
    ) -> DeliveryAssigneeResponse:
        assignee = await service.update(id, input)
        return DeliveryAssigneeResponse.from_orm_model(assignee)

    @strawberry.mutation
    @inject
    async def delete_delivery_assignee(
        self,
        id: UUID,
        service: Injected[DeliveryAssigneeService],
    ) -> bool:
        return await service.delete(id)
