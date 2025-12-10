"""Email status enum for campaign recipients."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class EmailStatus(IntEnum):
    """Status of an email sent to a campaign recipient."""

    PENDING = auto()
    SENT = auto()
    FAILED = auto()
    BOUNCED = auto()
