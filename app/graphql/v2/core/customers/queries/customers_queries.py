import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerResponse


@strawberry.type
class CustomersQueries:
    """GraphQL queries for Customers entity."""

    @strawberry.field
    @inject
    async def customer_search(
        self,
        service: Injected[CustomerService],
        search_term: str,
        published: bool = True,
        limit: int = 20,
    ) -> list[CustomerResponse]:
        """
        Search customers by company name.

        Args:
            search_term: The search term to match against company name
            published: Filter by published status (default: True)
            limit: Maximum number of customers to return (default: 20)

        Returns:
            List of CustomerResponse objects matching the search criteria
        """
        return CustomerResponse.from_orm_model_list(
            await service.search_customers(search_term, published, limit)
        )
