"""
Delivery enums for GraphQL.

Re-exports commons enums directly. Strawberry auto-registers Python enums.
No need to wrap with strawberry.enum() - use the commons enums directly in inputs/responses.
"""

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

__all__ = [
    "DeliveryDocumentType",
    "DeliveryIssueStatus",
    "DeliveryIssueType",
    "DeliveryItemStatus",
    "DeliveryReceiptType",
    "DeliveryStatus",
    "RecurringShipmentStatus",
    "WarehouseMemberRole",
]
