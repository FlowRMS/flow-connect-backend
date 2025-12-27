from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderInsideRep

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrderInsideRepResponse(DTOMixin[OrderInsideRep]):
    id: UUID
    user_id: UUID
    split_rate: Decimal
    position: int

    @classmethod
    def from_orm_model(cls, model: OrderInsideRep) -> Self:
        return cls(
            id=model.id,
            user_id=model.user_id,
            split_rate=model.split_rate,
            position=model.position,
        )
