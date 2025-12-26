from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_factory_sales_rep_service import (
    CustomerFactorySalesRepService,
)
from app.graphql.v2.core.customers.strawberry.customer_factory_sales_rep_response import (
    CustomerFactorySalesRepResponse,
)


@strawberry.type
class CustomerFactorySalesRepQueries:
    @strawberry.field
    @inject
    async def find_customer_factory_sales_rep_by_id(
        self,
        id: UUID,
        service: Injected[CustomerFactorySalesRepService],
    ) -> CustomerFactorySalesRepResponse:
        rep = await service.get_by_id(id)
        return CustomerFactorySalesRepResponse.from_orm_model(rep)

    @strawberry.field
    @inject
    async def list_customer_factory_sales_reps(
        self,
        customer_id: UUID,
        factory_id: UUID,
        service: Injected[CustomerFactorySalesRepService],
    ) -> list[CustomerFactorySalesRepResponse]:
        reps = await service.list_by_customer_and_factory(customer_id, factory_id)
        return CustomerFactorySalesRepResponse.from_orm_model_list(reps)
