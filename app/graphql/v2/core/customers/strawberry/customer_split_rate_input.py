import decimal
from uuid import UUID

import strawberry
from commons.db.v6 import CustomerSplitRate, RepTypeEnum

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class InsideSplitRateInput(BaseInputGQL[CustomerSplitRate]):
    user_id: UUID
    split_rate: decimal.Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> CustomerSplitRate:
        split_rate = CustomerSplitRate(
            user_id=self.user_id,
            rep_type=RepTypeEnum.INSIDE,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate


@strawberry.input
class OutsideSplitRateInput(BaseInputGQL[CustomerSplitRate]):
    user_id: UUID
    split_rate: decimal.Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> CustomerSplitRate:
        split_rate = CustomerSplitRate(
            user_id=self.user_id,
            rep_type=RepTypeEnum.OUTSIDE,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate
