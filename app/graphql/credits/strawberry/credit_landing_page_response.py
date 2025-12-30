from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.commission.credits.enums import CreditStatus, CreditType

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="CreditLandingPage")
class CreditLandingPageResponse(LandingPageInterfaceBase):
    credit_number: str
    status: CreditStatus
    credit_type: CreditType
    entity_date: date
    total: Decimal
    locked: bool
    reason: str | None
    order_id: str
    order_number: str
