from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_cpn_service import ProductCpnService
from app.graphql.v2.core.products.strawberry.product_cpn_response import (
    ProductCpnLiteResponse,
    ProductCpnResponse,
)


@strawberry.type
class ProductCpnQueries:
    @strawberry.field
    @inject
    async def product_cpn(
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

    @strawberry.field
    @inject
    async def product_cpn_by_product_id_and_customer_id(
        self,
        product_id: UUID,
        customer_id: UUID,
        service: Injected[ProductCpnService],
    ) -> ProductCpnLiteResponse | None:
        return ProductCpnLiteResponse.from_orm_model_optional(
            await service.find_cpn_by_product_and_customer(product_id, customer_id)
        )
