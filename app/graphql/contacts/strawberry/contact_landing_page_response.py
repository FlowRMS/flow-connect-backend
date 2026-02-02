"""Landing page response type for Contacts entity."""

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="ContactLandingPage")
class ContactLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for contacts with key fields for list views."""

    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str | None
    role_detail: str | None
    company_name: str | None
    tags: list[str] | None
