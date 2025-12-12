import uuid

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.products.services.product_service import ProductService
from app.graphql.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)
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
        product_category_id: strawberry.Maybe[uuid.UUID] = None,
        limit: int = 20,
    ) -> list[ProductResponse]:
        """
        Search products by factory part number.

        Args:
            search_term: The search term to match against factory part number
            factory_id: The UUID of the factory to filter products by (optional)
            product_category_id: The UUID of the product category to filter by (optional)
            limit: Maximum number of products to return (default: 20)

        Returns:
            List of ProductResponse objects matching the search criteria
        """
        factory_id_value = factory_id.value if factory_id else None
        product_category_id_value = (
            product_category_id.value if product_category_id else None
        )
        return ProductResponse.from_orm_model_list(
            await service.search_products(
                search_term, factory_id_value, product_category_id_value, limit
            )
        )

    @strawberry.field
    @inject
    async def product_category_search(
        self,
        service: Injected[ProductService],
        search_term: str,
        factory_id: strawberry.Maybe[uuid.UUID] = None,
        limit: int = 20,
    ) -> list[ProductCategoryResponse]:
        """
        Search product categories by title.

        Args:
            search_term: The search term to match against category title
            factory_id: The UUID of the factory to filter categories by (optional)
            limit: Maximum number of categories to return (default: 20)

        Returns:
            List of ProductCategoryResponse objects matching the search criteria
        """
        factory_id_value = factory_id.value if factory_id else None
        return ProductCategoryResponse.from_orm_model_list(
            await service.search_product_categories(
                search_term, factory_id_value, limit
            )
        )
