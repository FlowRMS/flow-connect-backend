from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.core.factories.models import FactoryV2
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class FactoryResponse(DTOMixin[FactoryV2]):
    _instance: strawberry.Private[FactoryV2]
    id: UUID
    title: str
    published: bool
    account_number: str | None
    email: str | None
    phone: str | None
    external_terms: str | None
    additional_information: str | None
    freight_terms: str | None
    freight_discount_type: int
    lead_time: str | None
    payment_terms: str | None
    commission_rate: Decimal | None
    commission_discount_rate: Decimal | None
    overall_discount_rate: Decimal | None
    logo_url: str | None
    inside_rep_id: UUID | None
    external_payment_terms: str | None
    commission_policy: int
    direct_commission_allowed: bool

    @classmethod
    def from_orm_model(cls, model: FactoryV2) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            title=model.title,
            published=model.published,
            account_number=model.account_number,
            email=model.email,
            phone=model.phone,
            external_terms=model.external_terms,
            additional_information=model.additional_information,
            freight_terms=model.freight_terms,
            freight_discount_type=model.freight_discount_type,
            lead_time=model.lead_time,
            payment_terms=model.payment_terms,
            commission_rate=model.commission_rate,
            commission_discount_rate=model.commission_discount_rate,
            overall_discount_rate=model.overall_discount_rate,
            logo_url=model.logo_url,
            inside_rep_id=model.inside_rep_id,
            external_payment_terms=model.external_payment_terms,
            commission_policy=model.commission_policy,
            direct_commission_allowed=model.direct_commission_allowed,
        )

    @strawberry.field
    async def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(
            await self._instance.awaitable_attrs.created_by
        )
