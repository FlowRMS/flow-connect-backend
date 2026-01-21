"""Landing page response type for PreOpportunity entity."""

from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_status import (
    PreOpportunityStatus,
)

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="PreOpportunityLandingPage")
class PreOpportunityLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for pre-opportunities with key fields for list views."""

    entity_number: str
    status: PreOpportunityStatus
    entity_date: date
    exp_date: date | None
    total: Decimal
    tags: list[str] | None
