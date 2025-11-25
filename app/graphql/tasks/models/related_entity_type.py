from enum import IntEnum, auto

import strawberry


@strawberry.enum
class RelatedEntityType(IntEnum):
    """Type of entity that can be related to a task."""

    JOB = auto()
    CONTACT = auto()
    COMPANY = auto()
