import strawberry

from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_lite_response import (
    FulfillmentOrderLineItemLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxItemResponse,
)


@strawberry.type
class FulfillmentOrderLineItemResponse(FulfillmentOrderLineItemLiteResponse):
    """Full response for line items - extends Lite with collections."""

    @strawberry.field
    def packing_box_items(self) -> list[PackingBoxItemResponse]:
        """Get packing box items - relationship is eager-loaded."""
        return PackingBoxItemResponse.from_orm_model_list(
            self._instance.packing_box_items
        )
