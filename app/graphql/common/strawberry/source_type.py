import enum
from enum import auto

import strawberry


@strawberry.enum
class SourceType(enum.IntEnum):
    CONTACT = auto()
    COMPANY = auto()
    JOB = auto()
    TASK = auto()
    NOTE = auto()
    CAMPAIGN = auto()
    QUOTE = auto()
    PRE_OPPORTUNITY = auto()
    SPEC_SHEET = auto()
    CUSTOMER = auto()
    FACTORY = auto()
    PRODUCT = auto()
    INVOICE = auto()
    ORDER = auto()
    CREDIT = auto()
    CHECK = auto()
    ADJUSTMENT = auto()
    ADDRESS = auto()
    SHIPPING_CARRIER = auto()
    CONTAINER_TYPE = auto()
    WAREHOUSE = auto()
    ORDER_ACKNOWLEDGEMENT = auto()
    FOLDER = auto()
