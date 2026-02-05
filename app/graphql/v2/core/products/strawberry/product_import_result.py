import strawberry

from app.graphql.v2.core.products.strawberry.product_import_error import (
    ProductImportError,
)


@strawberry.type
class ProductImportResult:
    success: bool
    products_created: int
    products_updated: int
    quantity_pricing_created: int
    customer_pricing_created: int
    customer_pricing_updated: int
    errors: list[ProductImportError]
    message: str
    # Customers that couldn't be found for CPN import
    customers_not_found: list[str]
