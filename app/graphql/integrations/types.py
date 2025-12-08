"""Strawberry GraphQL types for O365 integration."""

from datetime import datetime

import strawberry


@strawberry.type
class O365ConnectionStatusType:
    """Status of user's O365 connection."""

    is_connected: bool
    microsoft_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@strawberry.input
class O365SendEmailInput:
    """Input for sending an email via O365."""

    to: list[str]
    subject: str
    body: str
    body_type: str = "HTML"
    cc: list[str] | None = None
    bcc: list[str] | None = None


@strawberry.type
class O365SendEmailResultType:
    """Result of sending an email via O365."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@strawberry.type
class O365ConnectionResultType:
    """Result of OAuth connection."""

    success: bool
    microsoft_email: str | None = None
    error: str | None = None
