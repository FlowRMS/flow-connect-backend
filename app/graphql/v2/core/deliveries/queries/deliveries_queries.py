
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_service import DeliveryService
from app.graphql.v2.core.deliveries.strawberry.delivery_response import (
    DeliveryResponse,
)


@strawberry.type
class DeliveriesQueries:
    """GraphQL queries for Delivery entity."""

    @strawberry.field
    @inject
    async def deliveries(
        self,
        service: Injected[DeliveryService],
        warehouse_id: UUID | None = None,
    ) -> list[DeliveryResponse]:
        if warehouse_id:
            deliveries = await service.list_by_warehouse(warehouse_id)
        else:
            deliveries = await service.list_all()
        return DeliveryResponse.from_orm_model_list(deliveries)

    @strawberry.field
    @inject
    async def delivery(
        self,
        id: UUID,
        service: Injected[DeliveryService],
    ) -> DeliveryResponse:
        delivery = await service.get_by_id(id)
        return DeliveryResponse.from_orm_model(delivery)
