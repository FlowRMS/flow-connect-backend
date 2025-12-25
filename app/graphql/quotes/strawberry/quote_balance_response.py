from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteBalance

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class QuoteBalanceResponse(DTOMixin[QuoteBalance]):
    id: UUID
    quantity: Decimal
    subtotal: Decimal
    total: Decimal
    commission: Decimal
    discount: Decimal
    discount_rate: Decimal
    commission_rate: Decimal
    commission_discount: Decimal
    commission_discount_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: QuoteBalance) -> Self:
        return cls(
            id=model.id,
            quantity=model.quantity,
            subtotal=model.subtotal,
            total=model.total,
            commission=model.commission,
            discount=model.discount,
            discount_rate=model.discount_rate,
            commission_rate=model.commission_rate,
            commission_discount=model.commission_discount,
            commission_discount_rate=model.commission_discount_rate,
        )
