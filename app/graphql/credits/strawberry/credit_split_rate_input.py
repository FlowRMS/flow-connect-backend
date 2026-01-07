from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import CreditSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CreditSplitRateInput(BaseInputGQL[CreditSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> CreditSplitRate:
        split_rate = CreditSplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            split_rate.id = self.id
        return split_rate
