from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class OrderDetailToInvoiceDetailInput:
    quantity: Decimal
    unit_price: Decimal
    order_detail_id: UUID
