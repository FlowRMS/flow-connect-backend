from enum import IntEnum, auto

import strawberry


@strawberry.enum
class TaskPriority(IntEnum):
    """Priority level of a task."""

    LOW = auto()
    NORMAL = auto()
    URGENT = auto()
    CRITICAL = auto()
