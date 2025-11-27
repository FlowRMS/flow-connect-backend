from enum import IntEnum, auto

import strawberry


@strawberry.enum
class CompanyType(IntEnum):
    """Type of company in the CRM system."""

    CUSTOMER = auto()
    MANUFACTURER = auto()
