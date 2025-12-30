from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.shipment_requests.shipment_request_item import (
    ShipmentRequestItem,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ShipmentRequestItemResponse(DTOMixin[ShipmentRequestItem]):
    id: UUID
    request_id: UUID
    product_id: UUID
    quantity: Decimal
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
