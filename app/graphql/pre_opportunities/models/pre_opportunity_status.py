"""Pre-opportunity status enum."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class PreOpportunityStatus(IntEnum):
    """Status values for pre-opportunities."""

    QUALIFIED = auto()
    NEGOTIATION = auto()
    FOLLOW_UP = auto()
    WAITING_ON_FACTORY = auto()
    LOST = auto()
    WON = auto()
