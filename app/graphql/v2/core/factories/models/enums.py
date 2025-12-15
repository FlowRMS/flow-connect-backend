from enum import IntEnum, auto


class CommissionPolicyEnum(IntEnum):
    STANDARD = auto()
    CUSTOM = auto()


class FreightDiscountTypeEnum(IntEnum):
    NONE = auto()
    PERCENTAGE = auto()
