"""Campaign status enum."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class CampaignStatus(IntEnum):
    """Status of a campaign in the CRM system."""

    DRAFT = auto()
    SCHEDULED = auto()
    SENDING = auto()
    COMPLETED = auto()
    PAUSED = auto()
