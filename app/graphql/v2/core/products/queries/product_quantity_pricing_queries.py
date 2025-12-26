from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_quantity_pricing_service import (
    ProductQuantityPricingService,
)
from app.graphql.v2.core.products.strawberry.product_quantity_pricing_response import (
    ProductQuantityPricingResponse,
)


@strawberry.type
class ProductQuantityPricingQueries:
    @strawberry.field
    @inject
    async def product_quantity_pricing(
        self,
        id: UUID,
        service: Injected[ProductQuantityPricingService],
    ) -> ProductQuantityPricingResponse:
        pricing = await service.get_by_id(id)
        return ProductQuantityPricingResponse.from_orm_model(pricing)

    @strawberry.field
    @inject
    async def list_product_quantity_pricing_by_product_id(
        self,
        product_id: UUID,
        service: Injected[ProductQuantityPricingService],
    ) -> list[ProductQuantityPricingResponse]:
        pricing_list = await service.list_by_product_id(product_id)
        return ProductQuantityPricingResponse.from_orm_model_list(pricing_list)
