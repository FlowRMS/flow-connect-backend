from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import CreditDetail
from commons.db.v6.commission.credits.enums import CreditStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.credits.strawberry.credit_split_rate_response import (
    CreditSplitRateResponse,
)


@strawberry.type
class CreditDetailResponse(DTOMixin[CreditDetail]):
    _instance: strawberry.Private[CreditDetail]
    id: UUID
    credit_id: UUID
    order_detail_id: UUID | None
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    total: Decimal
    commission_rate: Decimal | None
    commission: Decimal | None
    status: CreditStatus

    @classmethod
    def from_orm_model(cls, model: CreditDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            credit_id=model.credit_id,
            order_detail_id=model.order_detail_id,
            item_number=model.item_number,
            quantity=model.quantity,
            unit_price=model.unit_price,
            subtotal=model.subtotal,
            total=model.total,
            commission_rate=model.commission_rate,
            commission=model.commission,
            status=model.status,
        )

    @strawberry.field
    def outside_split_rates(self) -> list[CreditSplitRateResponse]:
        return CreditSplitRateResponse.from_orm_model_list(
            self._instance.outside_split_rates
        )
