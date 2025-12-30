from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Deduction
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.deductions.strawberry.deduction_split_rate_response import (
    DeductionSplitRateResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class DeductionLiteResponse(DTOMixin[Deduction]):
    _instance: strawberry.Private[Deduction]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    check_id: UUID
    factory_id: UUID
    amount: Decimal
    reason: str | None
    creation_type: CreationType

    @classmethod
    def from_orm_model(cls, model: Deduction) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            check_id=model.check_id,
            factory_id=model.factory_id,
            amount=model.amount,
            reason=model.reason,
            creation_type=model.creation_type,
        )


@strawberry.type
class DeductionResponse(DeductionLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def split_rates(self) -> list[DeductionSplitRateResponse]:
        return DeductionSplitRateResponse.from_orm_model_list(
            self._instance.split_rates
        )
