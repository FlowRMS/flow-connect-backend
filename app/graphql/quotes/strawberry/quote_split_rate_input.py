from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class QuoteSplitRateInput(BaseInputGQL[QuoteSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> QuoteSplitRate:
        obj = QuoteSplitRate(
            user_id=self.user_id,
            position=self.position,
        )
        obj.split_rate = self.split_rate
        if self.id:
            obj.id = self.id
        return obj
