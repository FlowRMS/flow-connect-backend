from uuid import UUID

import strawberry

from app.graphql.v2.core.products.strawberry.product_cpn_import_item_input import (
    ProductCpnImportItemInput,
)


@strawberry.input
class ProductCpnImportInput:
    factory_id: UUID
    cpns: list[ProductCpnImportItemInput]
