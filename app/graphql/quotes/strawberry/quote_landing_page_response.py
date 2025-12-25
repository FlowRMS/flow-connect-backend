from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.crm.quotes import (
    PipelineStage,
    QuoteStatus,
)

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="QuoteLandingPage")
class QuoteLandingPageResponse(LandingPageInterfaceBase):
    quote_number: str
    status: QuoteStatus
    pipeline_stage: PipelineStage
    entity_date: date
    exp_date: date | None
    total: Decimal
    published: bool
