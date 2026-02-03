from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.factories.factory import Factory, OverageTypeEnum

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.factories.strawberry.factory_split_rate_input import (
    FactorySplitRateInput,
)


@strawberry.input
class FactoryInput(BaseInputGQL[Factory]):
    title: str
    split_rates: list[FactorySplitRateInput] = strawberry.field(default_factory=list)
    published: bool = False
    account_number: str | None = None
    email: str | None = None
    phone: str | None = None
    logo_id: UUID | None = None
    lead_time: int | None = None
    payment_terms: int | None = None
    base_commission_rate: Decimal = Decimal("0")
    commission_discount_rate: Decimal = Decimal("0")
    overall_discount_rate: Decimal = Decimal("0")
    additional_information: str | None = None
    freight_terms: str | None = None
    external_payment_terms: str | None = None
    is_parent: bool = False
    parent_id: UUID | None = None
    overage_allowed: bool = False
    overage_type: int = 0
    rep_overage_share: Decimal = Decimal("100.00")

    def to_orm_model(self) -> Factory:
        return Factory(
            title=self.title,
            published=self.published,
            account_number=self.account_number,
            email=self.email,
            phone=self.phone,
            logo_id=self.logo_id,
            lead_time=self.lead_time,
            payment_terms=self.payment_terms,
            base_commission_rate=self.base_commission_rate,
            commission_discount_rate=self.commission_discount_rate,
            overall_discount_rate=self.overall_discount_rate,
            additional_information=self.additional_information,
            freight_terms=self.freight_terms,
            external_payment_terms=self.external_payment_terms,
            is_parent=self.is_parent,
            parent_id=self.parent_id,
            overage_allowed=self.overage_allowed,
            overage_type=OverageTypeEnum(self.overage_type),
            rep_overage_share=self.rep_overage_share,
            split_rates=[rate.to_orm_model() for rate in self.split_rates],
        )
