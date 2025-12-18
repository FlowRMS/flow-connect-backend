from enum import IntEnum


class RbacResourceEnum(IntEnum):
    ADMIN = (1, True)
    FACTORY = 2
    CUSTOMER = 3
    PRODUCT = 4
    QUOTE = 5
    ORDER = 6
    INVOICE = 7
    CHECK = 8
    CREDIT = 9
    EXPENSE = 10
    JOB = 11
    PRE_OPPORTUNITY = 12
    TASK = 13

    def __new__(cls, value: int, immutable:bool = False):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.immutable = immutable
        return obj

    def __init__(self, num, immutable = False):
        self.num = num
        self.immutable = immutable
