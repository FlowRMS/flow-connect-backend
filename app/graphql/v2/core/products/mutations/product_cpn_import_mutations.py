import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_cpn_import_service import (
    ProductCpnImportService,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_input import (
    ProductCpnImportInput,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_result import (
    ProductCpnImportResult,
)


@strawberry.type
class ProductCpnImportMutations:
    @strawberry.mutation
    @inject
    async def import_product_cpns(
        self,
        input: ProductCpnImportInput,
        service: Injected[ProductCpnImportService],
    ) -> ProductCpnImportResult:
        return await service.import_cpns(input)
