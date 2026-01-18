from datetime import date
from decimal import Decimal

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="StatementLandingPage")
class StatementLandingPageResponse(LandingPageInterfaceBase):
    statement_number: str
    entity_date: date
    total: Decimal
    commission: Decimal
    factory_name: str
