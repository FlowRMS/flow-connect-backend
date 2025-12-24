from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class FactorySplitRateResponse(DTOMixin[FactorySplitRate]):
    _instance: strawberry.Private[FactorySplitRate]
    id: UUID
    factory_id: UUID
    position: int
    split_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: FactorySplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            factory_id=model.factory_id,
            position=model.position,
            split_rate=model.split_rate,
        )

    @strawberry.field
    def user(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.user)
