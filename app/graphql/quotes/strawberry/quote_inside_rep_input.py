from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteInsideRep

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class QuoteInsideRepInput(BaseInputGQL[QuoteInsideRep]):
    user_id: UUID
    split_rate: Decimal
    position: int = 0
    id: UUID | None = None

    def to_orm_model(self) -> QuoteInsideRep:
        inside_rep = QuoteInsideRep(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
        if self.id:
            inside_rep.id = self.id
        return inside_rep
