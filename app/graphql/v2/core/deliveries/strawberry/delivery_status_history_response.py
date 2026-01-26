from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryStatusHistory
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class DeliveryStatusHistoryResponse(DTOMixin[DeliveryStatusHistory]):
    """Response type for delivery status history."""

    _instance: strawberry.Private[DeliveryStatusHistory]
    id: UUID
    delivery_id: UUID
    status: DeliveryStatus
    timestamp: datetime
    user_id: UUID | None
    note: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryStatusHistory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            status=model.status,
            timestamp=model.timestamp,
            user_id=model.user_id,
            note=model.note,
        )
