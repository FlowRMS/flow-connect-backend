"""Send pace enum for campaigns."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class SendPace(IntEnum):
    """Send pace for campaign emails."""

    SLOW = auto()  # 25/hr
    MEDIUM = auto()  # 50/hr
    FAST = auto()  # 100/hr
