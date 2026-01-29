from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderInsideRep

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class OrderInsideRepInput(BaseInputGQL[OrderInsideRep]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> OrderInsideRep:
        obj = OrderInsideRep(
            user_id=self.user_id,
            position=self.position,
        )
        obj.split_rate = self.split_rate
        if self.id:
            obj.id = self.id
        return obj
