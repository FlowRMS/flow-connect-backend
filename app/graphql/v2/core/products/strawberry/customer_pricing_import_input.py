from decimal import Decimal

import strawberry


@strawberry.input
class CustomerPricingImportInput:
    customer_name: str
    customer_part_number: str | None = None  # Optional CPN code
    unit_price: Decimal
    commission_rate: Decimal
