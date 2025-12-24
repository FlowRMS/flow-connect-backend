from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import CustomerSplitRate, RepTypeEnum

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CustomerSplitRateResponse(DTOMixin[CustomerSplitRate]):
    _instance: strawberry.Private[CustomerSplitRate]
    id: UUID
    customer_id: UUID
    rep_type: RepTypeEnum
    position: int
    split_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: CustomerSplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            customer_id=model.customer_id,
            rep_type=model.rep_type,
            position=model.position,
            split_rate=model.split_rate,
        )

    @strawberry.field
    def user(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.user)
