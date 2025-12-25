import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="CustomerLandingPage")
class CustomerLandingPageResponse(LandingPageInterfaceBase):
    company_name: str
    published: bool
    is_parent: bool
    inside_reps: list[str]
    outside_reps: list[str]
