import uuid

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


@strawberry.type
class ProductsQueries:
    @strawberry.field
    @inject
    async def find_product_by_id(
        self,
        id: uuid.UUID,
        service: Injected[ProductService],
    ) -> ProductResponse:
        product = await service.get_by_id(id)
        return ProductResponse.from_orm_model(product)

    @strawberry.field
    @inject
    async def product_search(
        self,
        service: Injected[ProductService],
        search_term: str,
        product_category_ids: list[uuid.UUID] | None = None,
        factory_id: strawberry.Maybe[uuid.UUID] = None,
        limit: int = 20,
    ) -> list[ProductResponse]:
        factory_id_value = factory_id.value if factory_id else None
        return ProductResponse.from_orm_model_list(
            await service.search_products(
                search_term, factory_id_value, product_category_ids, limit
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
        factory_id_value = factory_id.value if factory_id else None
        return ProductCategoryResponse.from_orm_model_list(
            await service.search_product_categories(
                search_term, factory_id_value, limit
            )
        )
