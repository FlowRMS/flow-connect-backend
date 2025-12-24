import decimal
from uuid import UUID

import strawberry
from commons.db.v6 import CustomerSplitRate, RepTypeEnum

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CustomerSplitRateInput(BaseInputGQL[CustomerSplitRate]):
    user_id: UUID
    rep_type: RepTypeEnum
    split_rate: decimal.Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> CustomerSplitRate:
        split_rate = CustomerSplitRate(
            user_id=self.user_id,
            rep_type=self.rep_type,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate
