import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="CompanyLandingPage")
class CompanyLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for companies with key fields for list views."""

    name: str
    company_source_type: str
    website: str | None
    phone: str | None
    tags: list[str] | None
