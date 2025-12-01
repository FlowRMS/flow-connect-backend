"""Landing page response type for Notes entity."""

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="NoteLandingPage")
class NoteLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for notes with key fields for list views."""

    title: str
    content: str
    tags: list[str] | None
