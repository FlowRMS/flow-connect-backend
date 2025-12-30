import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_uom_service import ProductUomService
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class ProductUomQueries:
    @strawberry.field
    @inject
    async def product_uoms(
        self,
        service: Injected[ProductUomService],
    ) -> list[ProductUomResponse]:
        return ProductUomResponse.from_orm_model_list(await service.list_all())
