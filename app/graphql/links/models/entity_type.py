"""Entity type enum for link relations."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class EntityType(IntEnum):
    """Type of entity that can be linked in a link relation."""

    JOB = auto()
    TASK = auto()
    CONTACT = auto()
    COMPANY = auto()
    NOTE = auto()
    PRE_OPPORTUNITY = auto()
    QUOTE = auto()
    ORDER = auto()
    INVOICE = auto()
    CHECK = auto()
