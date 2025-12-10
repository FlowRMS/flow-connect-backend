"""Campaign repositories package."""

from app.graphql.campaigns.repositories.campaign_recipients_repository import (
    CampaignRecipientsRepository,
)
from app.graphql.campaigns.repositories.campaigns_repository import CampaignsRepository

__all__ = [
    "CampaignsRepository",
    "CampaignRecipientsRepository",
]
