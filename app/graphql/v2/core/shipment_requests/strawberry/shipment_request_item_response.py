from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from commons.db.v6.crm.shipment_requests.shipment_request_item import (
    ShipmentRequestItem,
)


@strawberry.type
class ShipmentRequestItemResponse(DTOMixin[ShipmentRequestItem]):
    id: UUID
    request_id: UUID
    product_id: str
    quantity: int
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: ShipmentRequestItem) -> Self:
        return cls(
            id=model.id,
            request_id=model.request_id,
            product_id=model.product_id,
            quantity=model.quantity,
            created_at=model.created_at,
        )
