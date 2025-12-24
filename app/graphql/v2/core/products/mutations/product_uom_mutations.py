from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_uom_service import ProductUomService
from app.graphql.v2.core.products.strawberry.product_uom_input import ProductUomInput
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class ProductUomMutations:
    @strawberry.mutation
    @inject
    async def create_product_uom(
        self,
        input: ProductUomInput,
        service: Injected[ProductUomService],
    ) -> ProductUomResponse:
        uom = await service.create(input)
        return ProductUomResponse.from_orm_model(uom)

    @strawberry.mutation
    @inject
    async def update_product_uom(
        self,
        id: UUID,
        input: ProductUomInput,
        service: Injected[ProductUomService],
    ) -> ProductUomResponse:
        uom = await service.update(id, input)
        return ProductUomResponse.from_orm_model(uom)

    @strawberry.mutation
    @inject
    async def delete_product_uom(
        self,
        id: UUID,
        service: Injected[ProductUomService],
    ) -> bool:
        return await service.delete(id)
