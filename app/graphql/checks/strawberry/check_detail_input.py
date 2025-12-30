from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import CheckDetail

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CheckDetailInput(BaseInputGQL[CheckDetail]):
    applied_amount: Decimal
    id: UUID | None = None
    invoice_id: UUID | None = None
    deduction_id: UUID | None = None
    credit_id: UUID | None = None

    def to_orm_model(self) -> CheckDetail:
        detail = CheckDetail(
            applied_amount=self.applied_amount,
            invoice_id=self.invoice_id,
            deduction_id=self.deduction_id,
            credit_id=self.credit_id,
        )
        if self.id:
            detail.id = self.id
        return detail
