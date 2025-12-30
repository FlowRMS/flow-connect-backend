from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import InvoiceSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class InvoiceSplitRateInput(BaseInputGQL[InvoiceSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> InvoiceSplitRate:
        split_rate = InvoiceSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate
