from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_import_service import (
    ProductImportService,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    ProductImportInput,
    ProductImportResult,
)


@strawberry.type
class ProductImportMutations:
    @strawberry.mutation
    @inject
    async def import_products(
        self,
        input: ProductImportInput,
        default_uom_id: UUID,
        service: Injected[ProductImportService],
    ) -> ProductImportResult:
        return await service.import_products(input, default_uom_id)
