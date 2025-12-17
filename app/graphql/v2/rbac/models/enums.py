from enum import IntEnum, auto


class RbacRoleEnum(IntEnum):
    OWNER = auto()
    ADMINISTRATOR = auto()
    INSIDE_REP = auto()
    OUTSIDE_REP = auto()
    WAREHOUSE_MANAGER = auto()
    WAREHOUSE_EMPLOYEE = auto()
    DRIVER = auto()

class RbacResourceEnum(IntEnum):
    ADMIN = auto()
    FACTORY = auto()
    CUSTOMER = auto()
    PRODUCT = auto()
    QUOTE = auto()
    ORDER = auto()
    INVOICE = auto()
    CHECK = auto()
    CREDIT = auto()
    EXPENSE = auto()
    JOB = auto()
    PRE_OPPORTUNITY = auto()
    TASK = auto()

class RbacPrivilegeTypeEnum(IntEnum):
    VIEW = auto()
    WRITE = auto()
    DELETE = auto()

class RbacPrivilegeOptionEnum(IntEnum):
    OWN = auto()
    ALL = auto()
