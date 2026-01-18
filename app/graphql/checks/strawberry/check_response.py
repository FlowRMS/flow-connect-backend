from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Check
from commons.db.v6.commission.checks.enums import CheckStatus
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.checks.strawberry.check_detail_response import CheckDetailResponse
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CheckLiteResponse(DTOMixin[Check]):
    _instance: strawberry.Private[Check]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    check_number: str
    entity_date: date
    post_date: date | None
    commission_month: date | None
    entered_commission_amount: Decimal | None
    factory_id: UUID
    status: CheckStatus
    creation_type: CreationType

    @classmethod
    def from_orm_model(cls, model: Check) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            check_number=model.check_number,
            entity_date=model.entity_date,
            post_date=model.post_date,
            commission_month=model.commission_month,
            entered_commission_amount=model.entered_commission_amount,
            factory_id=model.factory_id,
            status=model.status,
            creation_type=model.creation_type,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/commissions/list/{self.id}"


@strawberry.type
class CheckResponse(CheckLiteResponse):
    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def details(self) -> list[CheckDetailResponse]:
        return CheckDetailResponse.from_orm_model_list(self._instance.details)
