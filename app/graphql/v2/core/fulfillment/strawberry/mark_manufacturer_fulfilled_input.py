from uuid import UUID

import strawberry


@strawberry.input
class MarkManufacturerFulfilledInput:
    fulfillment_order_id: UUID
    line_item_ids: list[UUID]
