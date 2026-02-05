from uuid import UUID

import strawberry


@strawberry.input
class CancelBackorderInput:
    fulfillment_order_id: UUID
    line_item_ids: list[UUID]
    reason: str
