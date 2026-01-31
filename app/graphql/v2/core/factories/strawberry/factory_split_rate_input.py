import decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class FactorySplitRateInput(BaseInputGQL[FactorySplitRate]):
    user_id: UUID
    split_rate: decimal.Decimal
    position: int
    id: UUID | None = None

    def to_orm_model(self) -> FactorySplitRate:
        obj = FactorySplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            obj.id = self.id
        return obj
