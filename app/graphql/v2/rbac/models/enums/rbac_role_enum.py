from enum import IntEnum


class RbacRoleEnum(IntEnum):
    OWNER = (1, "owner", True)
    ADMINISTRATOR = (2, "administrator")
    INSIDE_REP = (3, "inside_rep")
    OUTSIDE_REP = (4, "outside_rep")
    WAREHOUSE_MANAGER = (5, "warehouse_manager")
    WAREHOUSE_EMPLOYEE = (6, "warehouse_employee")
    DRIVER = (7, "driver")

    def __new__(cls, value: int, label: str, immutable:bool = False):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        obj.immutable = immutable
        return obj

    def __init__(self, num, label, immutable = False):
        self.num = num
        self.label = label
        self.immutable = immutable

    def __str__(self):
        return self.label

    @classmethod
    def from_int(cls, num: int) -> "RbacRoleEnum | None":
        for role in cls:
            if role.num == num:
                return role
        return None

    @classmethod
    def from_label(cls, label: str) -> "RbacRoleEnum | None":
        for role in cls:
            if role.label == label:
                return role
        return None
