from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="AdjustmentLandingPage")
class AdjustmentLandingPageResponse(LandingPageInterfaceBase):
    adjustment_number: str
    status: AdjustmentStatus
    entity_date: date
    amount: Decimal
    locked: bool
    reason: str | None
