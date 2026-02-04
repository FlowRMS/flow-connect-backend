from dataclasses import dataclass
from datetime import datetime


class GmailAuthError(Exception):
    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass
class GmailConnectionStatus:
    is_connected: bool
    google_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass
class SendEmailResult:
    success: bool
    message_id: str | None = None
    error: str | None = None


@dataclass
class GmailConnectionResult:
    success: bool
    google_email: str | None = None
    error: str | None = None
