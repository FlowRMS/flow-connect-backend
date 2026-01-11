from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
    CustomerResponse,
)


@strawberry.type
class CustomersQueries:
    @strawberry.field
    @inject
    async def customer(
        self,
        service: Injected[CustomerService],
        id: UUID,
    ) -> CustomerResponse:
        customer = await service.get_by_id(id)
        return CustomerResponse.from_orm_model(customer)

    @strawberry.field
    @inject
    async def customer_search(
        self,
        service: Injected[CustomerService],
        search_term: str,
        published: bool = True,
        limit: int = 20,
    ) -> list[CustomerResponse]:
        return CustomerResponse.from_orm_model_list(
            await service.search_customers(search_term, published, limit)
        )

    @strawberry.field
    @inject
    async def customer_children(
        self,
        service: Injected[CustomerService],
        parent_id: UUID,
    ) -> list[CustomerLiteResponse]:
        children = await service.get_children(parent_id)
        return CustomerLiteResponse.from_orm_model_list(children)

    @strawberry.field
    @inject
    async def customer_buying_group_members(
        self,
        service: Injected[CustomerService],
        buying_group_id: UUID,
    ) -> list[CustomerLiteResponse]:
        members = await service.get_buying_group_members(buying_group_id)
        return CustomerLiteResponse.from_orm_model_list(members)
