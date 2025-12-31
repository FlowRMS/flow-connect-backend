from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import InvoiceBalance

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class InvoiceBalanceResponse(DTOMixin[InvoiceBalance]):
    id: UUID
    quantity: Decimal
    subtotal: Decimal
    total: Decimal
    commission: Decimal | None
    discount: Decimal
    discount_rate: Decimal
    commission_rate: Decimal | None
    commission_discount: Decimal | None
    commission_discount_rate: Decimal | None
    paid_balance: Decimal

    @classmethod
    def from_orm_model(cls, model: InvoiceBalance) -> Self:
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
            paid_balance=model.paid_balance,
        )
