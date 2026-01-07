from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import Credit
from commons.db.v6.commission.credits.enums import CreditStatus, CreditType
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.credits.strawberry.credit_balance_response import (
    CreditBalanceResponse,
)
from app.graphql.credits.strawberry.credit_detail_response import (
    CreditDetailResponse,
)
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CreditLiteResponse(DTOMixin[Credit]):
    _instance: strawberry.Private[Credit]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    credit_number: str
    entity_date: date
    reason: str | None
    order_id: UUID
    status: CreditStatus
    credit_type: CreditType
    locked: bool
    creation_type: CreationType
    balance_id: UUID

    @classmethod
    def from_orm_model(cls, model: Credit) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            credit_number=model.credit_number,
            entity_date=model.entity_date,
            reason=model.reason,
            order_id=model.order_id,
            status=model.status,
            credit_type=model.credit_type,
            locked=model.locked,
            creation_type=model.creation_type,
            balance_id=model.balance_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/credits/list/{self.id}"


@strawberry.type
class CreditCheckResponse(CreditLiteResponse):
    @strawberry.field
    def order(self) -> OrderLiteResponse:
        return OrderLiteResponse.from_orm_model(self._instance.order)


@strawberry.type
class CreditResponse(CreditLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def order(self) -> OrderLiteResponse:
        return OrderLiteResponse.from_orm_model(self._instance.order)

    @strawberry.field
    def balance(self) -> CreditBalanceResponse:
        return CreditBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[CreditDetailResponse]:
        return CreditDetailResponse.from_orm_model_list(self._instance.details)
