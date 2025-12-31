from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import AdjustmentSplitRate

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class AdjustmentSplitRateResponse(DTOMixin[AdjustmentSplitRate]):
    _instance: strawberry.Private[AdjustmentSplitRate]
    id: UUID
    adjustment_id: UUID
    user_id: UUID
    split_rate: Decimal | None
    position: int

    @classmethod
    def from_orm_model(cls, model: AdjustmentSplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            adjustment_id=model.adjustment_id,
            user_id=model.user_id,
            split_rate=model.split_rate,
            position=model.position,
        )

    @strawberry.field
    def user(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.user)
