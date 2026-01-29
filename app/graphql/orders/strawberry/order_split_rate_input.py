from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderSplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class OrderSplitRateInput(BaseInputGQL[OrderSplitRate]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> OrderSplitRate:
        obj = OrderSplitRate(
            user_id=self.user_id,
            position=self.position,
        )
        obj.split_rate = self.split_rate
        if self.id:
            obj.id = self.id
        return obj
