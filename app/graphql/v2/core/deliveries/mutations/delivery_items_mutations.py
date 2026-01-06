
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_item_service import (
    DeliveryItemService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import DeliveryItemInput
from app.graphql.v2.core.deliveries.strawberry.delivery_item_response import (
    DeliveryItemResponse,
)


@strawberry.type
class DeliveryItemsMutations:
    """GraphQL mutations for DeliveryItem entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_item(
        self,
        input: DeliveryItemInput,
        service: Injected[DeliveryItemService],
    ) -> DeliveryItemResponse:
        item = await service.create(input)
        return DeliveryItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def update_delivery_item(
        self,
        id: UUID,
        input: DeliveryItemInput,
        service: Injected[DeliveryItemService],
    ) -> DeliveryItemResponse:
        item = await service.update(id, input)
        return DeliveryItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def delete_delivery_item(
        self,
        id: UUID,
        service: Injected[DeliveryItemService],
    ) -> bool:
        return await service.delete(id)
