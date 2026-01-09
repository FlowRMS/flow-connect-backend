from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.shipment_requests import (
    ShipmentMethod,
    ShipmentPriority,
    ShipmentRequestStatus,
)


@strawberry.input
class ShipmentRequestItemInput:
    product_id: UUID
    quantity: Decimal


@strawberry.input
class CreateShipmentRequestInput:
    warehouse_id: UUID
    factory_id: UUID
    request_date: datetime
    priority: ShipmentPriority = ShipmentPriority.STANDARD
    method: ShipmentMethod | None = None
    status: ShipmentRequestStatus = ShipmentRequestStatus.PENDING
    notes: str | None = None
    items: list[ShipmentRequestItemInput] = strawberry.field(default_factory=list)


@strawberry.input
class UpdateShipmentRequestInput:
    id: UUID
    factory_id: UUID | None = None
    priority: ShipmentPriority | None = None
    method: ShipmentMethod | None = None
    status: ShipmentRequestStatus | None = None
    notes: str | None = None
    items: list[ShipmentRequestItemInput] | None = None
