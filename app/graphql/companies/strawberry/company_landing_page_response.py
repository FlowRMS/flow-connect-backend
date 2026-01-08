"""Landing page response type for Companies entity."""

import strawberry
from commons.db.v6.crm.companies.company_type import CompanyType

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="CompanyLandingPage")
class CompanyLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for companies with key fields for list views."""

    name: str
    company_source_type: CompanyType
    website: str | None
    phone: str | None
    tags: list[str] | None
