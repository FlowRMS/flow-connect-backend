"""Pre-opportunity status enum."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class PreOpportunityStatus(IntEnum):
    """Status values for pre-opportunities."""

    DRAFT = auto()
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    CONVERTED = auto()
