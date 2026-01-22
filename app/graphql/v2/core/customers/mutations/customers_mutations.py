from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_input import CustomerInput
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
    CustomerResponse,
)


@strawberry.type
class CustomersMutations:
    @strawberry.mutation
    @inject
    async def create_customer(
        self,
        input: CustomerInput,
        service: Injected[CustomerService],
    ) -> CustomerResponse:
        customer = await service.create(input)
        return CustomerResponse.from_orm_model(customer)

    @strawberry.mutation
    @inject
    async def update_customer(
        self,
        id: UUID,
        input: CustomerInput,
        service: Injected[CustomerService],
    ) -> CustomerResponse:
        customer = await service.update(id, input)
        return CustomerResponse.from_orm_model(customer)

    @strawberry.mutation
    @inject
    async def delete_customer(
        self,
        id: UUID,
        service: Injected[CustomerService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def assign_child_customers(
        self,
        parent_id: UUID,
        child_ids: list[UUID],
        service: Injected[CustomerService],
    ) -> list[CustomerLiteResponse]:
        children = await service.assign_children(parent_id, child_ids)
        return [CustomerLiteResponse.from_orm_model(child) for child in children]
