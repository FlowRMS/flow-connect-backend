from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class ProductCpnImportItemInput:
    factory_part_number: str
    customer_name: str
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal


@strawberry.input
class ProductCpnImportInput:
    factory_id: UUID
    cpns: list[ProductCpnImportItemInput]


@strawberry.type
class ProductCpnImportError:
    factory_part_number: str
    customer_name: str
    error: str


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
