from commons.db.v6.fulfillment import (
    CarrierType,
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentAssignment,
    FulfillmentAssignmentRole,
    FulfillmentMethod,
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    FulfillmentOrderStatus,
    PackingBox,
    PackingBoxItem,
)

from app.graphql.v2.core.fulfillment.mutations import FulfillmentMutations
from app.graphql.v2.core.fulfillment.queries import FulfillmentQueries
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentAssignmentRepository,
    FulfillmentLineRepository,
    FulfillmentOrderRepository,
    PackingBoxItemRepository,
    PackingBoxRepository,
)
from app.graphql.v2.core.fulfillment.services import (
    FulfillmentOrderService,
    FulfillmentPackingService,
    FulfillmentPickingService,
    FulfillmentShippingService,
)
from app.graphql.v2.core.fulfillment.strawberry import (
    AssignItemToBoxInput,
    AssignUserInput,
    BulkAssignmentInput,
    CompleteShippingInput,
    CreateFulfillmentLineItemInput,
    CreateFulfillmentOrderInput,
    CreatePackingBoxInput,
    FulfillmentActivityResponse,
    FulfillmentAssignmentResponse,
    FulfillmentOrderLineItemResponse,
    FulfillmentOrderResponse,
    FulfillmentStatsResponse,
    PackingBoxItemResponse,
    PackingBoxResponse,
    ShipToAddressInput,
    ShipToAddressResponse,
    UpdateFulfillmentOrderInput,
    UpdatePackingBoxInput,
    UpdatePickedQuantityInput,
)

__all__ = [
    # Models (from commons)
    "CarrierType",
    "FulfillmentActivity",
    "FulfillmentActivityType",
    "FulfillmentAssignment",
    "FulfillmentAssignmentRole",
    "FulfillmentMethod",
    "FulfillmentOrder",
    "FulfillmentOrderLineItem",
    "FulfillmentOrderStatus",
    "PackingBox",
    "PackingBoxItem",
    # Repositories
    "FulfillmentActivityRepository",
    "FulfillmentAssignmentRepository",
    "FulfillmentLineRepository",
    "FulfillmentOrderRepository",
    "PackingBoxItemRepository",
    "PackingBoxRepository",
    # Services
    "FulfillmentOrderService",
    "FulfillmentPackingService",
    "FulfillmentPickingService",
    "FulfillmentShippingService",
    # GraphQL Types - Responses
    "FulfillmentActivityResponse",
    "FulfillmentAssignmentResponse",
    "FulfillmentOrderLineItemResponse",
    "FulfillmentOrderResponse",
    "FulfillmentStatsResponse",
    "PackingBoxItemResponse",
    "PackingBoxResponse",
    "ShipToAddressResponse",
    # GraphQL Types - Inputs
    "AssignItemToBoxInput",
    "AssignUserInput",
    "BulkAssignmentInput",
    "CompleteShippingInput",
    "CreateFulfillmentLineItemInput",
    "CreateFulfillmentOrderInput",
    "CreatePackingBoxInput",
    "ShipToAddressInput",
    "UpdateFulfillmentOrderInput",
    "UpdatePackingBoxInput",
    "UpdatePickedQuantityInput",
    # GraphQL Operations
    "FulfillmentQueries",
    "FulfillmentMutations",
]
