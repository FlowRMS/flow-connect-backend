"""Strawberry enum registrations for fulfillment module."""

import strawberry
from commons.db.v6.fulfillment.enums import (
    CarrierType as _CarrierType,
    FulfillmentActivityType as _FulfillmentActivityType,
    FulfillmentAssignmentRole as _FulfillmentAssignmentRole,
    FulfillmentDocumentType as _FulfillmentDocumentType,
    FulfillmentMethod as _FulfillmentMethod,
    FulfillmentOrderStatus as _FulfillmentOrderStatus,
)

FulfillmentOrderStatus = strawberry.enum(_FulfillmentOrderStatus)
FulfillmentMethod = strawberry.enum(_FulfillmentMethod)
CarrierType = strawberry.enum(_CarrierType)
FulfillmentAssignmentRole = strawberry.enum(_FulfillmentAssignmentRole)
FulfillmentActivityType = strawberry.enum(_FulfillmentActivityType)
FulfillmentDocumentType = strawberry.enum(_FulfillmentDocumentType)

__all__ = [
    "FulfillmentOrderStatus",
    "FulfillmentMethod",
    "CarrierType",
    "FulfillmentAssignmentRole",
    "FulfillmentActivityType",
    "FulfillmentDocumentType",
]
