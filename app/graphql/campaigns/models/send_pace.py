"""Send pace enum for campaigns."""

from enum import IntEnum, auto

import strawberry


@strawberry.enum
class SendPace(IntEnum):
    """Send pace for campaign emails."""

    SLOW = auto()      # 50/hr
    MEDIUM = auto()    # 200/hr
    FAST = auto()      # 500/hr
