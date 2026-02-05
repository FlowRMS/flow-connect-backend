import strawberry

from app.graphql.v2.core.products.strawberry.product_cpn_import_error import (
    ProductCpnImportError,
)


@strawberry.type
class ProductCpnImportResult:
    success: bool
    cpns_created: int
    cpns_updated: int
    errors: list[ProductCpnImportError]
    message: str
    # Lookup failures (products or customers not found)
    products_not_found: list[str]
    customers_not_found: list[str]
