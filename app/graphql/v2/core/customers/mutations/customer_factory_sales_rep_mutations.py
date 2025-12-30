from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_factory_sales_rep_service import (
    CustomerFactorySalesRepService,
)
from app.graphql.v2.core.customers.strawberry.customer_factory_sales_rep_input import (
    CustomerFactorySalesRepInput,
)
from app.graphql.v2.core.customers.strawberry.customer_factory_sales_rep_response import (
    CustomerFactorySalesRepResponse,
)


@strawberry.type
class CustomerFactorySalesRepMutations:
    @strawberry.mutation
    @inject
    async def create_customer_factory_sales_rep(
        self,
        input: CustomerFactorySalesRepInput,
        service: Injected[CustomerFactorySalesRepService],
    ) -> CustomerFactorySalesRepResponse:
        rep = await service.create(input)
        return CustomerFactorySalesRepResponse.from_orm_model(rep)

    @strawberry.mutation
    @inject
    async def update_customer_factory_sales_rep(
        self,
        id: UUID,
        input: CustomerFactorySalesRepInput,
        service: Injected[CustomerFactorySalesRepService],
    ) -> CustomerFactorySalesRepResponse:
        rep = await service.update(id, input)
        return CustomerFactorySalesRepResponse.from_orm_model(rep)

    @strawberry.mutation
    @inject
    async def delete_customer_factory_sales_rep(
        self,
        id: UUID,
        service: Injected[CustomerFactorySalesRepService],
    ) -> bool:
        return await service.delete(id)
