from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.commission.checks.enums import CheckStatus

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="CheckLandingPage")
class CheckLandingPageResponse(LandingPageInterfaceBase):
    check_number: str
    status: CheckStatus
    post_date: date | None
    entered_commission_amount: Decimal | None
    commission_month: date | None
    factory_name: str
