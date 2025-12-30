from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import CheckDetail

from app.core.db.adapters.dto import DTOMixin
from app.graphql.adjustments.strawberry.adjustment_response import (
    AdjustmentLiteResponse,
)
from app.graphql.credits.strawberry.credit_response import CreditLiteResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceLiteResponse


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
    def invoice(self) -> InvoiceLiteResponse | None:
        return InvoiceLiteResponse.from_orm_model_optional(self._instance.invoice)

    @strawberry.field
    def adjustment(self) -> AdjustmentLiteResponse | None:
        return AdjustmentLiteResponse.from_orm_model_optional(self._instance.adjustment)

    @strawberry.field
    def credit(self) -> CreditLiteResponse | None:
        return CreditLiteResponse.from_orm_model_optional(self._instance.credit)
