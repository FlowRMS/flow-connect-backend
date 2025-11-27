"""Landing page response type for PreOpportunity entity."""

from datetime import date
from decimal import Decimal

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="PreOpportunityLandingPage")
class PreOpportunityLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for pre-opportunities with key fields for list views."""

    entity_number: str
    status: str
    entity_date: date
    exp_date: date | None
    total: Decimal
