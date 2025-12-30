from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import DeductionSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeductionSplitRateInput(BaseInputGQL[DeductionSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> DeductionSplitRate:
        split_rate = DeductionSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate
