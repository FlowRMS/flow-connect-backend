from enum import IntEnum, auto

import strawberry


@strawberry.enum
class TaskStatus(IntEnum):
    """Status of a task in the CRM system."""

    TODO = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()
