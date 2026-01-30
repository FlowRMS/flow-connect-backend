from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.statements import CommissionStatementBalance

from app.core.db.adapters.dto import DTOMixin

# Default value for decimal fields that might be None in legacy data
_ZERO = Decimal("0")


@strawberry.type
class StatementBalanceResponse(DTOMixin[CommissionStatementBalance]):
    id: UUID
    quantity: Decimal
    subtotal: Decimal
    total: Decimal
    commission: Decimal | None
    discount: Decimal
    discount_rate: Decimal
    commission_rate: Decimal
    commission_discount: Decimal
    commission_discount_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: CommissionStatementBalance) -> Self:
        return cls(
            id=model.id,
            quantity=model.quantity or _ZERO,
            subtotal=model.subtotal or _ZERO,
            total=model.total or _ZERO,
            commission=model.commission,
            discount=model.discount or _ZERO,
            discount_rate=model.discount_rate or _ZERO,
            commission_rate=model.commission_rate or _ZERO,
            commission_discount=model.commission_discount or _ZERO,
            commission_discount_rate=model.commission_discount_rate or _ZERO,
        )
