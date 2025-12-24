from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerResponse


@strawberry.type
class CustomersQueries:
    @strawberry.field
    @inject
    async def find_customer_by_id(
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
