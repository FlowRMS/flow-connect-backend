
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_item_service import (
    DeliveryItemService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_item_response import (
    DeliveryItemResponse,
)


@strawberry.type
class DeliveryItemsQueries:
    """GraphQL queries for DeliveryItem entity."""

    @strawberry.field
    @inject
    async def delivery_items(
        self,
        delivery_id: UUID,
        service: Injected[DeliveryItemService],
    ) -> list[DeliveryItemResponse]:
        items = await service.list_by_delivery(delivery_id)
        return DeliveryItemResponse.from_orm_model_list(items)

    @strawberry.field
    @inject
    async def delivery_item(
        self,
        id: UUID,
        service: Injected[DeliveryItemService],
    ) -> DeliveryItemResponse:
        item = await service.get_by_id(id)
        return DeliveryItemResponse.from_orm_model(item)
