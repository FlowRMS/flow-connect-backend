from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core import Factory

from app.core.db.adapters.dto import DTOMixin
from app.graphql.common.strawberry.overage_record import OverageTypeEnum
from app.graphql.v2.core.factories.strawberry.factory_split_rate_response import (
    FactorySplitRateResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class FactoryLiteResponse(DTOMixin[Factory]):
    _instance: strawberry.Private[Factory]
    id: UUID
    title: str
    published: bool
    freight_discount_type: int
    account_number: str | None
    email: str | None
    phone: str | None
    logo_id: UUID | None
    lead_time: int | None
    payment_terms: int | None
    base_commission_rate: Decimal | None
    commission_discount_rate: Decimal | None
    overall_discount_rate: Decimal
    additional_information: str | None
    freight_terms: str | None
    external_payment_terms: str | None
    is_parent: bool
    parent_id: UUID | None
    overage_allowed: bool
    overage_type: OverageTypeEnum
    rep_overage_share: Decimal

    @classmethod
    def from_orm_model(cls, model: Factory) -> Self:
        # DB enum: BY_LINE=0, BY_TOTAL=1
        overage_type_map = {
            0: OverageTypeEnum.BY_LINE,
            1: OverageTypeEnum.BY_TOTAL,
        }
        return cls(
            _instance=model,
            id=model.id,
            title=model.title,
            published=model.published,
            freight_discount_type=model.freight_discount_type,
            account_number=model.account_number,
            email=model.email,
            phone=model.phone,
            logo_id=model.logo_id,
            lead_time=model.lead_time,
            payment_terms=model.payment_terms,
            base_commission_rate=model.base_commission_rate,
            commission_discount_rate=model.commission_discount_rate,
            overall_discount_rate=model.overall_discount_rate,
            additional_information=model.additional_information,
            freight_terms=model.freight_terms,
            external_payment_terms=model.external_payment_terms,
            is_parent=model.is_parent,
            parent_id=model.parent_id,
            overage_allowed=model.overage_allowed,
            overage_type=overage_type_map.get(
                int(model.overage_type), OverageTypeEnum.BY_LINE
            ),
            rep_overage_share=model.rep_overage_share,
        )


@strawberry.type
class FactoryResponse(FactoryLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def split_rates(self) -> list[FactorySplitRateResponse]:
        return FactorySplitRateResponse.from_orm_model_list(self._instance.split_rates)

    @strawberry.field
    def parent(self) -> "FactoryLiteResponse | None":
        if not self._instance.parent:
            return None
        return FactoryLiteResponse.from_orm_model(self._instance.parent)
