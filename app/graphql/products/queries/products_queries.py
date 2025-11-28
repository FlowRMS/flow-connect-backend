import uuid

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.products.services.product_service import ProductService
from app.graphql.products.strawberry.product_response import ProductResponse


@strawberry.type
class ProductsQueries:
    """GraphQL queries for Products entity."""

    @strawberry.field
    @inject
    async def product_search(
        self,
        service: Injected[ProductService],
        search_term: str,
        factory_id: strawberry.Maybe[uuid.UUID] = None,
        limit: int = 20,
    ) -> list[ProductResponse]:
        """
        Search products by factory part number.

        Args:
            search_term: The search term to match against factory part number
            limit: Maximum number of products to return (default: 20)

        Returns:
            List of ProductResponse objects matching the search criteria
        """
        factory_id_value = factory_id.value if factory_id else None
        return ProductResponse.from_orm_model_list(
            await service.search_products(search_term, factory_id_value, limit)
        )
