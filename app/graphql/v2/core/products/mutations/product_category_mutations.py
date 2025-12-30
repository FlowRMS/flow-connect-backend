from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_category_service import (
    ProductCategoryService,
)
from app.graphql.v2.core.products.strawberry.product_category_input import (
    ProductCategoryInput,
)
from app.graphql.v2.core.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)


@strawberry.type
class ProductCategoryMutations:
    @strawberry.mutation
    @inject
    async def create_product_category(
        self,
        input: ProductCategoryInput,
        service: Injected[ProductCategoryService],
    ) -> ProductCategoryResponse:
        category = await service.create(input)
        return ProductCategoryResponse.from_orm_model(category)

    @strawberry.mutation
    @inject
    async def update_product_category(
        self,
        id: UUID,
        input: ProductCategoryInput,
        service: Injected[ProductCategoryService],
    ) -> ProductCategoryResponse:
        category = await service.update(id, input)
        return ProductCategoryResponse.from_orm_model(category)

    @strawberry.mutation
    @inject
    async def delete_product_category(
        self,
        id: UUID,
        service: Injected[ProductCategoryService],
    ) -> bool:
        return await service.delete(id)
