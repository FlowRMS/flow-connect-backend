from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_input import ProductInput
from app.graphql.v2.core.products.strawberry.product_response import ProductResponse


@strawberry.type
class ProductsMutations:
    @strawberry.mutation
    @inject
    async def create_product(
        self,
        input: ProductInput,
        service: Injected[ProductService],
    ) -> ProductResponse:
        product = await service.create(input)
        return ProductResponse.from_orm_model(product)

    @strawberry.mutation
    @inject
    async def update_product(
        self,
        id: UUID,
        input: ProductInput,
        service: Injected[ProductService],
    ) -> ProductResponse:
        product = await service.update(id, input)
        return ProductResponse.from_orm_model(product)

    @strawberry.mutation
    @inject
    async def delete_product(
        self,
        id: UUID,
        service: Injected[ProductService],
    ) -> bool:
        return await service.delete(id)
