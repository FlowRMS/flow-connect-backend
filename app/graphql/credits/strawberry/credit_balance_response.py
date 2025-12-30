from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import CreditBalance

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class CreditBalanceResponse(DTOMixin[CreditBalance]):
    id: UUID
    quantity: Decimal
    subtotal: Decimal
    total: Decimal
    commission: Decimal

    @classmethod
    def from_orm_model(cls, model: CreditBalance) -> Self:
        return cls(
            id=model.id,
            quantity=model.quantity,
            subtotal=model.subtotal,
            total=model.total,
            commission=model.commission,
        )
