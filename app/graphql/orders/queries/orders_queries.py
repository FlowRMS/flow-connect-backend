from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.orders.strawberry.order_response import OrderResponse


@strawberry.type
class OrdersQueries:
    @strawberry.field
    @inject
    async def order(
        self,
        id: UUID,
        service: Injected[OrderService],
    ) -> OrderResponse:
        order = await service.find_order_by_id(id)
        return OrderResponse.from_orm_model(order)

    @strawberry.field
    @inject
    async def order_search(
        self,
        service: Injected[OrderService],
        search_term: str,
        limit: int = 20,
    ) -> list[OrderLiteResponse]:
        return OrderLiteResponse.from_orm_model_list(
            await service.search_orders(search_term, limit)
        )
