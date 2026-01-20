from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class QuoteDetailToOrderDetailInput:
    quantity: Decimal
    unit_price: Decimal
    quote_detail_id: UUID
