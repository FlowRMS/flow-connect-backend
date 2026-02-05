from decimal import Decimal

import strawberry


@strawberry.input
class ProductCpnImportItemInput:
    factory_part_number: str
    customer_name: str
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal
