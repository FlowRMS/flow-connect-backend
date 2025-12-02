import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_response import OrderResponse


@strawberry.type
class OrdersQueries:
    """GraphQL queries for Orders entity."""

    @strawberry.field
    @inject
    async def order_search(
        self,
        service: Injected[OrderService],
        search_term: str,
        limit: int = 20,
    ) -> list[OrderResponse]:
        """
        Search orders by order number.

        Args:
            search_term: The search term to match against order number
            limit: Maximum number of orders to return (default: 20)

        Returns:
            List of OrderResponse objects matching the search criteria
        """
        return OrderResponse.from_orm_model_list(
            await service.search_orders(search_term, limit)
        )
