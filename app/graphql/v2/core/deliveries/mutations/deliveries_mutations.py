
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_service import DeliveryService
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryInput
from app.graphql.v2.core.deliveries.strawberry.delivery_response import (
    DeliveryResponse,
)


@strawberry.type
class DeliveriesMutations:
    """GraphQL mutations for Delivery entity."""

    @strawberry.mutation
    @inject
    async def create_delivery(
        self,
        input: DeliveryInput,
        service: Injected[DeliveryService],
    ) -> DeliveryResponse:
        delivery = await service.create(input)
        return DeliveryResponse.from_orm_model(delivery)

    @strawberry.mutation
    @inject
    async def update_delivery(
        self,
        id: UUID,
        input: DeliveryInput,
        service: Injected[DeliveryService],
    ) -> DeliveryResponse:
        delivery = await service.update(id, input)
        return DeliveryResponse.from_orm_model(delivery)

    @strawberry.mutation
    @inject
    async def delete_delivery(
        self,
        id: UUID,
        service: Injected[DeliveryService],
    ) -> bool:
        return await service.delete(id)
