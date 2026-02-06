from enum import StrEnum


class ExchangeFileStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"


class ValidationStatus(StrEnum):
    NOT_VALIDATED = "not_validated"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"


class ReceivedExchangeFileStatus(StrEnum):
    NEW = "new"
    DOWNLOADED = "downloaded"
