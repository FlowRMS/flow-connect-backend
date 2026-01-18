from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.territories.territory_split_rate import TerritorySplitRate

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class TerritorySplitRateResponse(DTOMixin[TerritorySplitRate]):
    _instance: strawberry.Private[TerritorySplitRate]
    id: UUID
    territory_id: UUID
    user_id: UUID
    split_rate: Decimal
    position: int

    @classmethod
    def from_orm_model(cls, model: TerritorySplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            territory_id=model.territory_id,
            user_id=model.user_id,
            split_rate=model.split_rate,
            position=model.position,
        )

    @strawberry.field
    def user(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.user)
