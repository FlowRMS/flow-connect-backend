"""Types for product import from CSV."""

from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class QuantityPricingImportInput:
    """Input for a single quantity pricing band."""

    quantity_low: Decimal
    quantity_high: Decimal | None  # None means "and above"
    unit_price: Decimal


@strawberry.input
class ProductImportItemInput:
    """Input for a single product to import."""

    factory_part_number: str
    unit_price: Decimal
    description: str | None = None
    upc: str | None = None
    category: str | None = None
    default_commission_rate: Decimal | None = None
    quantity_pricing: list[QuantityPricingImportInput] | None = None


@strawberry.input
class ProductImportInput:
    """Input for bulk product import."""

    factory_id: UUID
    products: list[ProductImportItemInput]


@strawberry.type
class ProductImportError:
    """Error details for a single product that failed to import."""

    factory_part_number: str
    error: str


@strawberry.type
class ProductImportResult:
    """Result of a bulk product import operation."""

    success: bool
    products_created: int
    products_updated: int
    quantity_pricing_created: int
    errors: list[ProductImportError]
    message: str
