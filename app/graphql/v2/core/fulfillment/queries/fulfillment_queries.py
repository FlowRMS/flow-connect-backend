from uuid import UUID

import strawberry
from aioinject import Injected

from commons.db.v6.fulfillment import FulfillmentOrderStatus

from app.graphql.inject import inject
from app.graphql.v2.core.fulfillment.services import FulfillmentOrderService
from app.graphql.v2.core.fulfillment.strawberry import (
    FulfillmentOrderResponse,
    FulfillmentStatsResponse,
)


@strawberry.type
class FulfillmentQueries:
    @strawberry.field
    @inject
    async def fulfillment_orders(
        self,
        service: Injected[FulfillmentOrderService],
        warehouse_id: UUID | None = None,
        status: list[FulfillmentOrderStatus] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FulfillmentOrderResponse]:
        orders = await service.list_orders(
            warehouse_id=warehouse_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )
        return FulfillmentOrderResponse.from_orm_model_list(orders)

    @strawberry.field
    @inject
    async def fulfillment_order(
        self,
        id: UUID,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse | None:
        order = await service.get_by_id(id)
        return FulfillmentOrderResponse.from_orm_model_optional(order)

    @strawberry.field
    @inject
    async def fulfillment_stats(
        self,
        service: Injected[FulfillmentOrderService],
        warehouse_id: UUID | None = None,
    ) -> FulfillmentStatsResponse:
        stats = await service.get_stats(warehouse_id)
        return FulfillmentStatsResponse(
            pending_count=stats["pending"],
            in_progress_count=stats["in_progress"],
            completed_count=stats["completed"],
            backorder_count=stats["backorder"],
        )
