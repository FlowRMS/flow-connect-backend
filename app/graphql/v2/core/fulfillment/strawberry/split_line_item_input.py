from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class SplitLineItemInput:
    line_item_id: UUID
    warehouse_qty: Decimal
    manufacturer_qty: Decimal
