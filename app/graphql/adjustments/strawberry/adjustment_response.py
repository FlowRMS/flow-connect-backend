from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Adjustment
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.adjustments.strawberry.adjustment_split_rate_response import (
    AdjustmentSplitRateResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class AdjustmentLiteResponse(DTOMixin[Adjustment]):
    _instance: strawberry.Private[Adjustment]
    id: UUID
    adjustment_number: str
    status: AdjustmentStatus
    locked: bool
    entity_date: date
    created_at: datetime
    created_by_id: UUID
    factory_id: UUID
    amount: Decimal
    reason: str | None
    creation_type: CreationType

    @classmethod
    def from_orm_model(cls, model: Adjustment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            adjustment_number=model.adjustment_number,
            entity_date=model.entity_date,
            status=model.status,
            locked=model.locked,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            factory_id=model.factory_id,
            amount=model.amount,
            reason=model.reason,
            creation_type=model.creation_type,
        )


@strawberry.type
class AdjustmentResponse(AdjustmentLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def customer(self) -> CustomerLiteResponse | None:
        return CustomerLiteResponse.from_orm_model_optional(self._instance.customer)

    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def split_rates(self) -> list[AdjustmentSplitRateResponse]:
        return AdjustmentSplitRateResponse.from_orm_model_list(
            self._instance.split_rates
        )
