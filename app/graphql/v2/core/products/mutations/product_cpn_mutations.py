from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_cpn_service import ProductCpnService
from app.graphql.v2.core.products.strawberry.product_cpn_input import ProductCpnInput
from app.graphql.v2.core.products.strawberry.product_cpn_response import (
    ProductCpnResponse,
)


@strawberry.type
class ProductCpnMutations:
    @strawberry.mutation
    @inject
    async def create_product_cpn(
        self,
        input: ProductCpnInput,
        service: Injected[ProductCpnService],
    ) -> ProductCpnResponse:
        cpn = await service.create(input)
        return ProductCpnResponse.from_orm_model(cpn)

    @strawberry.mutation
    @inject
    async def update_product_cpn(
        self,
        id: UUID,
        input: ProductCpnInput,
        service: Injected[ProductCpnService],
    ) -> ProductCpnResponse:
        cpn = await service.update(id, input)
        return ProductCpnResponse.from_orm_model(cpn)

    @strawberry.mutation
    @inject
    async def delete_product_cpn(
        self,
        id: UUID,
        service: Injected[ProductCpnService],
    ) -> bool:
        return await service.delete(id)
