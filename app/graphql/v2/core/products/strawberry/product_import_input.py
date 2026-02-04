from uuid import UUID

import strawberry

from app.graphql.v2.core.products.strawberry.product_import_item_input import (
    ProductImportItemInput,
)


@strawberry.input
class ProductImportInput:
    factory_id: UUID
    products: list[ProductImportItemInput]
