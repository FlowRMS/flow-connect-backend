from enum import StrEnum


class OrgType(StrEnum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    REP_FIRM = "rep_firm"
    ASSOCIATION = "association"
    ADMIN_ORG = "admin_org"

    def get_complementary_type(self) -> "OrgType":
        if self == OrgType.MANUFACTURER:
            return OrgType.DISTRIBUTOR
        return OrgType.MANUFACTURER


class OrgStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
