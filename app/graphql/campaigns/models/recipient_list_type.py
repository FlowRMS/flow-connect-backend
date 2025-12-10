"""Recipient list type enum for campaigns."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class RecipientListType(IntEnum):
    """Type of recipient list for a campaign."""

    STATIC = auto()
    CRITERIA_BASED = auto()
    DYNAMIC = auto()
