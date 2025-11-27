"""Landing page response type for Jobs entity."""

from datetime import date

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="JobLandingPage")
class JobLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for jobs with key fields for list views."""

    job_name: str
    status_name: str
    start_date: date | None
    end_date: date | None
    description: str | None
    job_type: str | None
    requester: str | None
    job_owner: str | None
