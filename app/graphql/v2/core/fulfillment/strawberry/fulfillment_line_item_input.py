from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrderLineItem

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CreateFulfillmentLineItemInput(BaseInputGQL[FulfillmentOrderLineItem]):
    product_id: UUID
    ordered_qty: Decimal
    order_detail_id: UUID | None = None

    def to_orm_model(self) -> FulfillmentOrderLineItem:
        item = FulfillmentOrderLineItem(
            ordered_qty=self.ordered_qty,
        )
        item.product_id = self.product_id
        item.order_detail_id = self.order_detail_id
        return item


@strawberry.input
class UpdatePickedQuantityInput:
    line_item_id: UUID
    quantity: Decimal
    notes: str | None = None


@strawberry.input
class MarkManufacturerFulfilledInput:
    """Input for marking line items as manufacturer fulfilled."""

    fulfillment_order_id: UUID
    line_item_ids: list[UUID]


@strawberry.input
class SplitLineItemInput:
    """Input for splitting a line item between warehouse and manufacturer."""

    line_item_id: UUID
    warehouse_qty: Decimal
    manufacturer_qty: Decimal


@strawberry.input
class CancelBackorderInput:
    """Input for cancelling backorder items."""

    fulfillment_order_id: UUID
    line_item_ids: list[UUID]
    reason: str
