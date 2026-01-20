from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.territories.territory_split_rate import TerritorySplitRate

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class TerritorySplitRateInput(BaseInputGQL[TerritorySplitRate]):
    id: UUID | None = None
    user_id: UUID
    split_rate: Decimal
    position: int

    def to_orm_model(self) -> TerritorySplitRate:
        return TerritorySplitRate(
            user_id=self.user_id,
            split_rate=self.split_rate,
            position=self.position,
        )
