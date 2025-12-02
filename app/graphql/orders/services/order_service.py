from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Order

from app.graphql.orders.repositories.orders_repository import OrdersRepository


class OrderService:
    """Service for Orders entity business logic."""

    def __init__(
        self,
        repository: OrdersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_orders(self, search_term: str, limit: int = 20) -> list[Order]:
        """
        Search orders by order number.

        Args:
            search_term: The search term to match against order number
            limit: Maximum number of orders to return (default: 20)

        Returns:
            List of Order objects matching the search criteria
        """
        return await self.repository.search_by_order_number(search_term, limit)

    async def find_orders_by_job_id(self, job_id: UUID) -> list[Order]:
        """Find all orders linked to the given job ID."""
        return await self.repository.find_by_job_id(job_id)
