from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class QuantityPricingImportInput:
    quantity_low: Decimal
    quantity_high: Decimal | None  # None means "and above"
    unit_price: Decimal


@strawberry.input
class CustomerPricingImportInput:
    customer_name: str
    customer_part_number: str | None = None  # Optional CPN code
    unit_price: Decimal
    commission_rate: Decimal


@strawberry.input
class ProductImportItemInput:
    factory_part_number: str
    unit_price: Decimal
    description: str | None = None
    upc: str | None = None
    category: str | None = None
    default_commission_rate: Decimal | None = None
    quantity_pricing: list[QuantityPricingImportInput] | None = None
    customer_pricing: list[CustomerPricingImportInput] | None = None


@strawberry.input
class ProductImportInput:
    factory_id: UUID
    products: list[ProductImportItemInput]


@strawberry.type
class ProductImportError:
    factory_part_number: str
    error: str


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
