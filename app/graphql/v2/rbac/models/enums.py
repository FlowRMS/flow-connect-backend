from enum import IntEnum, Enum


class RbacRoleEnum(Enum):
    OWNER = (1, "owner")
    ADMINISTRATOR = (2, "administrator")
    INSIDE_REP = (3, "inside_rep")
    OUTSIDE_REP = (4, "outside_rep")
    WAREHOUSE_MANAGER = (5, "warehouse_manager")
    WAREHOUSE_EMPLOYEE = (6, "warehouse_employee")
    DRIVER = (7, "driver")

    def __init__(self, num, label):
        self.num = num
        self.label = label

    def __str__(self):
        return self.label

    @classmethod
    def from_int(cls, num: int) -> "RbacRoleEnum | None":
        for role in cls:
            if role.num == num:
                return role
        return None

class RbacResourceEnum(IntEnum):
    ADMIN = 1
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

class RbacPrivilegeTypeEnum(IntEnum):
    VIEW = 1
    WRITE = 2
    DELETE = 3

class RbacPrivilegeOptionEnum(IntEnum):
    OWN = 1
    ALL = 2
