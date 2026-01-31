from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import AdjustmentSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class AdjustmentSplitRateInput(BaseInputGQL[AdjustmentSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> AdjustmentSplitRate:
        obj = AdjustmentSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            obj.id = self.id
        return obj
