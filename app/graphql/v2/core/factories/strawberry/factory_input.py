from decimal import Decimal
from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.factories.models import (
    CommissionPolicyEnum,
    FactoryV2,
    FreightDiscountTypeEnum,
)


@strawberry.input
class FactoryInput(BaseInputGQL[FactoryV2]):
    title: str
    published: bool = False
    account_number: str | None = None
    email: str | None = None
    phone: str | None = None
    external_terms: str | None = None
    additional_information: str | None = None
    freight_terms: str | None = None
    freight_discount_type: FreightDiscountTypeEnum = FreightDiscountTypeEnum.NONE
    lead_time: str | None = None
    payment_terms: str | None = None
    commission_rate: Decimal | None = None
    commission_discount_rate: Decimal | None = None
    overall_discount_rate: Decimal | None = None
    logo_url: str | None = None
    inside_rep_id: UUID | None = None
    external_payment_terms: str | None = None
    commission_policy: CommissionPolicyEnum = CommissionPolicyEnum.STANDARD
    direct_commission_allowed: bool = True

    def to_orm_model(self) -> FactoryV2:
        return FactoryV2(
            title=self.title,
            published=self.published,
            account_number=self.account_number,
            email=self.email,
            phone=self.phone,
            external_terms=self.external_terms,
            additional_information=self.additional_information,
            freight_terms=self.freight_terms,
            freight_discount_type=self.freight_discount_type,
            lead_time=self.lead_time,
            payment_terms=self.payment_terms,
            commission_rate=self.commission_rate,
            commission_discount_rate=self.commission_discount_rate,
            overall_discount_rate=self.overall_discount_rate,
            logo_url=self.logo_url,
            inside_rep_id=self.inside_rep_id,
            external_payment_terms=self.external_payment_terms,
            commission_policy=self.commission_policy,
            direct_commission_allowed=self.direct_commission_allowed,
        )
