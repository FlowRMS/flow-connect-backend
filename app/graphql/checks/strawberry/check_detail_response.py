from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import CheckDetail

from app.core.db.adapters.dto import DTOMixin
from app.graphql.adjustments.strawberry.adjustment_response import (
    AdjustmentCheckResponse,
)
from app.graphql.credits.strawberry.credit_response import CreditCheckResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceCheckResponse


@strawberry.type
class CheckDetailResponse(DTOMixin[CheckDetail]):
    _instance: strawberry.Private[CheckDetail]
    id: UUID
    check_id: UUID
    invoice_id: UUID | None
    adjustment_id: UUID | None
    credit_id: UUID | None
    applied_amount: Decimal

    @classmethod
    def from_orm_model(cls, model: CheckDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            check_id=model.check_id,
            invoice_id=model.invoice_id,
            adjustment_id=model.adjustment_id,
            credit_id=model.credit_id,
            applied_amount=model.applied_amount,
        )

    @strawberry.field
    def invoice(self) -> InvoiceCheckResponse | None:
        return InvoiceCheckResponse.from_orm_model_optional(self._instance.invoice)

    @strawberry.field
    def adjustment(self) -> AdjustmentCheckResponse | None:
        return AdjustmentCheckResponse.from_orm_model_optional(
            self._instance.adjustment
        )

    @strawberry.field
    def credit(self) -> CreditCheckResponse | None:
        return CreditCheckResponse.from_orm_model_optional(self._instance.credit)
