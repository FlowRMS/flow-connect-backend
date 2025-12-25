from datetime import date
from decimal import Decimal

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="QuoteLandingPage")
class QuoteLandingPageResponse(LandingPageInterfaceBase):
    quote_number: str
    status: str
    pipeline_stage: str
    entity_date: date
    exp_date: date | None
    total: Decimal
    published: bool
