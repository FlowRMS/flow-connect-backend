from enum import IntEnum, auto

import strawberry


@strawberry.enum
class AIEntityType(IntEnum):
    QUOTES = auto()
    ORDERS = auto()
    INVOICES = auto()
    CHECKS = auto()
    UNDEFINED = auto()
    ORDER_ACKNOWLEDGEMENTS = auto()
    CUSTOMERS = auto()
    FACTORIES = auto()
    PRODUCTS = auto()
    END_USERS = auto()


@strawberry.enum
class FileType(IntEnum):
    TXT = auto()
    PDF = auto()
    TABULAR = auto()


@strawberry.enum
class ProcessingStatus(IntEnum):
    PENDING_REVIEW = auto()
    IN_REVISION = auto()
    APPROVED = auto()
    REJECTED = auto()
    AUTO_APPROVED = auto()
    SKIPPED = auto()
