from decimal import Decimal
from uuid import UUID

import strawberry


@strawberry.input
class UpdatePickedQuantityInput:
    line_item_id: UUID
    quantity: Decimal
    notes: str | None = None
