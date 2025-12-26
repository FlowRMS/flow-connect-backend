from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_quantity_pricing_service import (
    ProductQuantityPricingService,
)
from app.graphql.v2.core.products.strawberry.product_quantity_pricing_input import (
    ProductQuantityPricingInput,
)
from app.graphql.v2.core.products.strawberry.product_quantity_pricing_response import (
    ProductQuantityPricingResponse,
)


@strawberry.type
class ProductQuantityPricingMutations:
    @strawberry.mutation
    @inject
    async def create_product_quantity_pricing(
        self,
        input: ProductQuantityPricingInput,
        service: Injected[ProductQuantityPricingService],
    ) -> ProductQuantityPricingResponse:
        pricing = await service.create(input)
        return ProductQuantityPricingResponse.from_orm_model(pricing)

    @strawberry.mutation
    @inject
    async def update_product_quantity_pricing(
        self,
        id: UUID,
        input: ProductQuantityPricingInput,
        service: Injected[ProductQuantityPricingService],
    ) -> ProductQuantityPricingResponse:
        pricing = await service.update(id, input)
        return ProductQuantityPricingResponse.from_orm_model(pricing)

    @strawberry.mutation
    @inject
    async def delete_product_quantity_pricing(
        self,
        id: UUID,
        service: Injected[ProductQuantityPricingService],
    ) -> bool:
        return await service.delete(id)
