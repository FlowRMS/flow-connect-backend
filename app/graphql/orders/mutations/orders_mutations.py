from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_input import OrderInput
from app.graphql.orders.strawberry.order_response import OrderResponse


@strawberry.type
class OrdersMutations:
    @strawberry.mutation
    @inject
    async def create_order(
        self,
        input: OrderInput,
        service: Injected[OrderService],
    ) -> OrderResponse:
        order = await service.create_order(order_input=input)
        return OrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def update_order(
        self,
        input: OrderInput,
        service: Injected[OrderService],
    ) -> OrderResponse:
        order = await service.update_order(order_input=input)
        return OrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def delete_order(
        self,
        id: UUID,
        service: Injected[OrderService],
    ) -> bool:
        return await service.delete_order(order_id=id)
