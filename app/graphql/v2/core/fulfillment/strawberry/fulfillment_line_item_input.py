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
            allocated_qty=self.ordered_qty,  # Initialize allocated_qty to ordered_qty
        )
        item.product_id = self.product_id
        item.order_detail_id = self.order_detail_id
        return item
