from datetime import date
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

    @strawberry.mutation
    @inject
    async def create_order_from_quote(
        self,
        quote_id: UUID,
        order_number: str,
        factory_id: UUID,
        service: Injected[OrderService],
        due_date: date | None = None,
        quote_detail_ids: list[UUID] | None = None,
    ) -> OrderResponse:
        order = await service.create_order_from_quote(
            quote_id=quote_id,
            order_number=order_number,
            factory_id=factory_id,
            due_date=due_date,
            quote_detail_ids=quote_detail_ids,
        )
        return OrderResponse.from_orm_model(order)

    @strawberry.mutation
    @inject
    async def duplicate_order(
        self,
        order_id: UUID,
        new_order_number: str,
        new_sold_to_customer_id: UUID,
        service: Injected[OrderService],
    ) -> OrderResponse:
        order = await service.duplicate_order(
            order_id=order_id,
            new_order_number=new_order_number,
            new_sold_to_customer_id=new_sold_to_customer_id,
        )
        return OrderResponse.from_orm_model(order)
