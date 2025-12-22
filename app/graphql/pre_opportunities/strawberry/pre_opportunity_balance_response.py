"""GraphQL response type for PreOpportunityBalance (read-only)."""

from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class PreOpportunityBalanceResponse(DTOMixin[PreOpportunityBalance]):
    """Read-only balance totals for a pre-opportunity."""

    id: UUID
    subtotal: Decimal
    total: Decimal
    quantity: Decimal
    discount: Decimal
    discount_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: PreOpportunityBalance) -> Self:
        return cls(
            id=model.id,
            subtotal=model.subtotal,
            total=model.total,
            quantity=model.quantity,
            discount=model.discount,
            discount_rate=model.discount_rate,
        )
