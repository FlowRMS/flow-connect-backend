from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from commons.db.v6.fulfillment.enums import FulfillmentOrderStatus
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentBackorderService,
    FulfillmentOrderService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    FulfillmentOrderLineItemResponse,
    FulfillmentOrderResponse,
    FulfillmentStatsResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_lite_response import (
    FulfillmentOrderLineItemLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_lite_response import (
    FulfillmentOrderLiteResponse,
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
    ) -> list[FulfillmentOrderLiteResponse]:
        """List fulfillment orders - uses Lite response for efficient loading."""
        orders = await service.list_orders(
            warehouse_id=warehouse_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )
        return FulfillmentOrderLiteResponse.from_orm_model_list(orders)

    @strawberry.field
    @inject
    async def fulfillment_order(
        self,
        id: UUID,
        service: Injected[FulfillmentOrderService],
    ) -> FulfillmentOrderResponse | None:
        """Get a single fulfillment order - uses Full response with collections."""
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

    @strawberry.field
    @inject
    async def backorder_items(
        self,
        fulfillment_order_id: UUID,
        service: Injected[FulfillmentBackorderService],
    ) -> list[FulfillmentOrderLineItemLiteResponse]:
        """Get all line items with backorder quantities for a fulfillment order."""
        items = await service.get_backorder_items(fulfillment_order_id)
        return FulfillmentOrderLineItemLiteResponse.from_orm_model_list(items)
