# Input types
# Response types
from app.graphql.v2.core.fulfillment.strawberry.add_assignment_input import (
    AddAssignmentInput,
)
from app.graphql.v2.core.fulfillment.strawberry.add_document_input import (
    AddDocumentInput,
)
from app.graphql.v2.core.fulfillment.strawberry.assign_user_input import (
    AssignUserInput,
)
from app.graphql.v2.core.fulfillment.strawberry.bulk_assignment_input import (
    BulkAssignmentInput,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_activity_response import (
    FulfillmentActivityResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_assignment_response import (
    FulfillmentAssignmentResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_document_response import (
    FulfillmentDocumentResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_input import (
    CancelBackorderInput,
    CreateFulfillmentLineItemInput,
    LinkShipmentRequestInput,
    MarkManufacturerFulfilledInput,
    SplitLineItemInput,
    UpdatePickedQuantityInput,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_lite_response import (
    FulfillmentOrderLineItemLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_response import (
    FulfillmentOrderLineItemResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_input import (
    CompleteShippingInput,
    CreateFulfillmentOrderInput,
    UpdateFulfillmentOrderInput,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_lite_response import (
    FulfillmentOrderLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_order_response import (
    FulfillmentOrderResponse,
    ShipToAddressResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_stats_response import (
    FulfillmentStatsResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_input import (
    AssignItemToBoxInput,
    CreatePackingBoxInput,
    UpdatePackingBoxInput,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxItemResponse,
    PackingBoxResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.upload_document_input import (
    UploadDocumentInput,
)

__all__ = [
    # Input types
    "AddAssignmentInput",
    "AddDocumentInput",
    "AssignItemToBoxInput",
    "AssignUserInput",
    "BulkAssignmentInput",
    "CancelBackorderInput",
    "CompleteShippingInput",
    "CreateFulfillmentLineItemInput",
    "CreateFulfillmentOrderInput",
    "CreatePackingBoxInput",
    "LinkShipmentRequestInput",
    "MarkManufacturerFulfilledInput",
    "SplitLineItemInput",
    "UpdateFulfillmentOrderInput",
    "UpdatePackingBoxInput",
    "UpdatePickedQuantityInput",
    "UploadDocumentInput",
    # Response types
    "FulfillmentActivityResponse",
    "FulfillmentAssignmentResponse",
    "FulfillmentDocumentResponse",
    "FulfillmentOrderLineItemLiteResponse",
    "FulfillmentOrderLineItemResponse",
    "FulfillmentOrderLiteResponse",
    "FulfillmentOrderResponse",
    "FulfillmentStatsResponse",
    "PackingBoxItemResponse",
    "PackingBoxResponse",
    "ShipToAddressResponse",
]
