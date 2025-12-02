from commons.auth import AuthInfo
from commons.db.models import Customer

from app.graphql.customers.repositories.customers_repository import CustomersRepository


class CustomerService:
    """Service for Customers entity business logic."""

    def __init__(
        self,
        repository: CustomersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_customers(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Customer]:
        """
        Search customers by company name.

        Args:
            search_term: The search term to match against company name
            published: Filter by published status (default: True)
            limit: Maximum number of customers to return (default: 20)

        Returns:
            List of Customer objects matching the search criteria
        """
        return await self.repository.search_by_company_name(
            search_term, published, limit
        )
