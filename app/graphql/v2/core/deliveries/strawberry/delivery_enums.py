
from enum import IntEnum

import strawberry


@strawberry.enum
class DeliveryStatusGQL(IntEnum):
    DRAFT = 1
    PENDING = 2
    CONFIRMED = 3
    ARRIVED = 4
    RECEIVING = 5
    RECEIVED = 6
    CANCELLED = 7


@strawberry.enum
class RecurringShipmentStatusGQL(IntEnum):
    ACTIVE = 1
    PAUSED = 2
    CANCELLED = 3


@strawberry.enum
class DeliveryItemStatusGQL(IntEnum):
    PENDING = 1
    RECEIVED = 2
    PARTIAL = 3
    DISCREPANCY = 4


@strawberry.enum
class DeliveryIssueTypeGQL(IntEnum):
    DAMAGED = 1
    MISSING = 2
    OVERAGE = 3
    WRONG_ITEM = 4
    OTHER = 5


@strawberry.enum
class DeliveryIssueStatusGQL(IntEnum):
    OPEN = 1
    COMMUNICATED = 2
    RESOLVED = 3
    CLOSED = 4


@strawberry.enum
class DeliveryDocumentTypeGQL(IntEnum):
    PACKING_SLIP = 1
    BOL = 2
    PHOTO = 3
    OTHER = 4


@strawberry.enum
class DeliveryReceiptTypeGQL(IntEnum):
    RECEIPT = 1
    ADJUSTMENT = 2
    RETURN = 3


@strawberry.enum
class DeliveryAssigneeRoleGQL(IntEnum):
    WORKER = 1
    MANAGER = 2
