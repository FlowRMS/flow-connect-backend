
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryItemReceipt

from app.core.db.adapters.dto import DTOMixin

from .delivery_enums import DeliveryReceiptTypeGQL


@strawberry.type
class DeliveryItemReceiptResponse(DTOMixin[DeliveryItemReceipt]):
    """Response type for delivery item receipts."""

    _instance: strawberry.Private[DeliveryItemReceipt]
    id: UUID
    delivery_item_id: UUID
    receipt_type: DeliveryReceiptTypeGQL
    received_qty: int
    damaged_qty: int
    location_id: UUID | None
    received_by_id: UUID | None
    received_at: datetime | None
    note: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryItemReceipt) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_item_id=model.delivery_item_id,
            receipt_type=DeliveryReceiptTypeGQL(model.receipt_type.value),
            received_qty=model.received_qty,
            damaged_qty=model.damaged_qty,
            location_id=model.location_id,
            received_by_id=model.received_by_id,
            received_at=model.received_at,
            note=model.note,
        )
