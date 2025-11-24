from enum import IntEnum, auto

import strawberry


@strawberry.enum
class JobStatus(IntEnum):
    BID = auto()
    BUY = auto()
    COMPLETE = auto()
