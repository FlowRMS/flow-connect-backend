from uuid import UUID

import strawberry


@strawberry.input
class LinkShipmentRequestInput:
    fulfillment_order_id: UUID
    line_item_ids: list[UUID]
    shipment_request_id: UUID
