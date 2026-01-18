"""
Delivery enums for GraphQL.

Uses commons enums as single source of truth, registered with Strawberry for GraphQL.
"""

import strawberry
from commons.db.v6.warehouse.deliveries.delivery_enums import (
    DeliveryDocumentType,
    DeliveryIssueStatus,
    DeliveryIssueType,
    DeliveryItemStatus,
    DeliveryReceiptType,
    DeliveryStatus,
    RecurringShipmentStatus,
)
from commons.db.v6.warehouse.warehouse_member_role import WarehouseMemberRole

# Register commons enums for GraphQL
DeliveryStatusEnum = strawberry.enum(DeliveryStatus)
RecurringShipmentStatusEnum = strawberry.enum(RecurringShipmentStatus)
DeliveryItemStatusEnum = strawberry.enum(DeliveryItemStatus)
DeliveryIssueTypeEnum = strawberry.enum(DeliveryIssueType)
DeliveryIssueStatusEnum = strawberry.enum(DeliveryIssueStatus)
DeliveryDocumentTypeEnum = strawberry.enum(DeliveryDocumentType)
DeliveryReceiptTypeEnum = strawberry.enum(DeliveryReceiptType)
DeliveryAssigneeRoleEnum = strawberry.enum(WarehouseMemberRole)
