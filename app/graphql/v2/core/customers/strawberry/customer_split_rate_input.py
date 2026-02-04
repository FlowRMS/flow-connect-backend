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
        obj = CustomerSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            rep_type=RepTypeEnum.INSIDE,
            position=self.position,
        )
        if self.id:
            obj.id = self.id
        return obj


@strawberry.input
class OutsideSplitRateInput(BaseInputGQL[CustomerSplitRate]):
    user_id: UUID
    split_rate: decimal.Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> CustomerSplitRate:
        obj = CustomerSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            rep_type=RepTypeEnum.OUTSIDE,
            position=self.position,
        )
        if self.id:
            obj.id = self.id
        return obj
