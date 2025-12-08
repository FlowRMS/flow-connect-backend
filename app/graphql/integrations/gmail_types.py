"""Strawberry GraphQL types for Gmail integration."""

from datetime import datetime

import strawberry


@strawberry.type
class GmailConnectionStatusType:
    """Status of user's Gmail connection."""

    is_connected: bool
    google_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@strawberry.input
class GmailSendEmailInput:
    """Input for sending an email via Gmail."""

    to: list[str]
    subject: str
    body: str
    body_type: str = "HTML"
    cc: list[str] | None = None
    bcc: list[str] | None = None


@strawberry.type
class GmailSendEmailResultType:
    """Result of sending an email via Gmail."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@strawberry.type
class GmailConnectionResultType:
    """Result of OAuth connection."""

    success: bool
    google_email: str | None = None
    error: str | None = None
