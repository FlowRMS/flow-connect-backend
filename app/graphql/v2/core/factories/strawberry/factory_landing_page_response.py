from decimal import Decimal

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="FactoryLandingPage")
class FactoryLandingPageResponse(LandingPageInterfaceBase):
    title: str
    published: bool
    freight_discount_type: int
    account_number: str | None
    email: str | None
    phone: str | None
    lead_time: int | None
    payment_terms: int | None
    base_commission_rate: Decimal | None
    commission_discount_rate: Decimal | None
    overall_discount_rate: Decimal
    split_rates: list[str]
    is_parent: bool
    parent: str | None
    overage_allowed: bool
    overage_type: int
    rep_overage_share: Decimal
