from enum import StrEnum


class ConnectionStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    ACCEPTED = "active"  # Remote DB uses "active" for accepted connections
    DECLINED = "declined"
