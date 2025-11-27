from enum import IntEnum, auto

import strawberry


@strawberry.enum
class AddressType(IntEnum):
    """Type of address in the CRM system."""

    BILLING = auto()
    SHIPPING = auto()
    OTHER = auto()
