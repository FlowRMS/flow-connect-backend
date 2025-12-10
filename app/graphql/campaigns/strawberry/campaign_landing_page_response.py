"""Landing page response type for Campaigns entity."""

from datetime import datetime

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.recipient_list_type import RecipientListType


@strawberry.type(name="CampaignLandingPage")
class CampaignLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for campaigns with key fields for list views."""

    name: str
    status: CampaignStatus
    recipient_list_type: RecipientListType
    recipients_count: int
    sent_count: int
    scheduled_at: strawberry.Private[datetime | None] = None

    @strawberry.field
    def progress(self) -> str:
        """Return progress as sent/total format."""
        return f"{self.sent_count} / {self.recipients_count}"
