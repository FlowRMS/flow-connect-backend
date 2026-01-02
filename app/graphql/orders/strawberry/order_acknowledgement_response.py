from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderAcknowledgement
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrderAcknowledgementResponse(DTOMixin[OrderAcknowledgement]):
    _instance: strawberry.Private[OrderAcknowledgement]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    order_id: UUID
    order_detail_id: UUID
    order_acknowledgement_number: str
    entity_date: date
    quantity: Decimal
    ship_date: date | None
    creation_type: CreationType

    @classmethod
    def from_orm_model(cls, model: OrderAcknowledgement) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            order_id=model.order_id,
            order_detail_id=model.order_detail_id,
            order_acknowledgement_number=model.order_acknowledgement_number,
            entity_date=model.entity_date,
            quantity=model.quantity,
            ship_date=model.ship_date,
            creation_type=model.creation_type,
        )
