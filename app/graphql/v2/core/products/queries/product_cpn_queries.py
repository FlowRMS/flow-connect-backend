from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_cpn_service import ProductCpnService
from app.graphql.v2.core.products.strawberry.product_cpn_response import (
    ProductCpnResponse,
)


@strawberry.type
class ProductCpnQueries:
    @strawberry.field
    @inject
    async def find_product_cpn_by_id(
        self,
        id: UUID,
        service: Injected[ProductCpnService],
    ) -> ProductCpnResponse:
        cpn = await service.get_by_id(id)
        return ProductCpnResponse.from_orm_model(cpn)

    @strawberry.field
    @inject
    async def list_product_cpns_by_product_id(
        self,
        product_id: UUID,
        service: Injected[ProductCpnService],
    ) -> list[ProductCpnResponse]:
        cpns = await service.list_by_product_id(product_id)
        return ProductCpnResponse.from_orm_model_list(cpns)
