from decimal import Decimal

import strawberry

from app.graphql.v2.core.products.strawberry.customer_pricing_import_input import (
    CustomerPricingImportInput,
)
from app.graphql.v2.core.products.strawberry.quantity_pricing_import_input import (
    QuantityPricingImportInput,
)


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
