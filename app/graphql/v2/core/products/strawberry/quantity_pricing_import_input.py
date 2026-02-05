from decimal import Decimal

import strawberry


@strawberry.input
class QuantityPricingImportInput:
    quantity_low: Decimal
    quantity_high: Decimal | None  # None means "and above"
    unit_price: Decimal
