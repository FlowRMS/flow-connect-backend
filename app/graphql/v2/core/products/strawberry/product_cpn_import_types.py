"""Types for product CPN (Customer Part Number) bulk import."""

from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class ProductCpnImportItemInput:
    """Input for a single CPN to import.

    Uses factory_part_number for product lookup and customer_name for customer lookup.
    The backend will resolve these to the appropriate UUIDs.
    """

    factory_part_number: str
    customer_name: str
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal


@strawberry.input
class ProductCpnImportInput:
    """Input for bulk CPN import."""

    factory_id: UUID
    cpns: list[ProductCpnImportItemInput]


@strawberry.type
class ProductCpnImportError:
    """Error details for a single CPN that failed to import."""

    factory_part_number: str
    customer_name: str
    error: str


@strawberry.type
class ProductCpnImportResult:
    """Result of a bulk CPN import operation."""

    success: bool
    cpns_created: int
    cpns_updated: int
    errors: list[ProductCpnImportError]
    message: str
    # Lookup failures (products or customers not found)
    products_not_found: list[str]
    customers_not_found: list[str]
