from dataclasses import dataclass
from enum import Enum, auto

from commons.auth import AuthInfo

from app.integrations.gmail.services.gmail_auth_service import (
    GmailAuthService,
)
from app.integrations.gmail.services.gmail_auth_service import (
    SendEmailResult as GmailSendResult,
)
from app.integrations.microsoft_o365.services.o365_auth_service import (
    O365AuthService,
)
from app.integrations.microsoft_o365.services.o365_auth_service import (
    SendEmailResult as O365SendResult,
)


class EmailProvider(Enum):
    """Available email providers."""

    O365 = auto()
    GMAIL = auto()


@dataclass
class EmailAttachment:
    """Represents an email attachment."""

    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass
class SendEmailResult:
    """Unified result of sending an email."""

    success: bool
    message_id: str | None = None
    error: str | None = None
    provider: EmailProvider | None = None


@dataclass
class EmailProviderStatus:
    """Status of available email providers for a user."""

    o365_connected: bool
    gmail_connected: bool
    preferred_provider: EmailProvider | None = None


class EmailProviderService:
    """
    Service to send emails using the user's connected email provider.

    Abstracts away O365 and Gmail, automatically selecting the available provider.
    """

    def __init__(
        self,
        o365_service: O365AuthService,
        gmail_service: GmailAuthService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.o365_service = o365_service
        self.gmail_service = gmail_service
        self.auth_info = auth_info

    async def get_provider_status(self) -> EmailProviderStatus:
        """Check which email providers are connected for the current user."""
        o365_status = await self.o365_service.get_connection_status()
        gmail_status = await self.gmail_service.get_connection_status()

        preferred = None
        if o365_status.is_connected:
            preferred = EmailProvider.O365
        elif gmail_status.is_connected:
            preferred = EmailProvider.GMAIL

        return EmailProviderStatus(
            o365_connected=o365_status.is_connected,
            gmail_connected=gmail_status.is_connected,
            preferred_provider=preferred,
        )

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        body_type: str = "HTML",
        provider: EmailProvider | None = None,
        attachments: list[EmailAttachment] | None = None,
    ) -> SendEmailResult:
        """
        Send an email using the specified or available provider.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: Body content type ("HTML" or "Text")
            provider: Specific provider to use, or None for auto-selection
            attachments: Optional list of file attachments

        Returns:
            SendEmailResult with success status and details
        """
        status = await self.get_provider_status()

        # Determine which provider to use
        if provider is None:
            provider = status.preferred_provider

        if provider is None:
            return SendEmailResult(
                success=False,
                error="No email provider connected. Please connect O365 or Gmail.",
            )

        # Send via the selected provider
        if provider == EmailProvider.O365:
            if not status.o365_connected:
                return SendEmailResult(
                    success=False,
                    error="O365 is not connected.",
                    provider=EmailProvider.O365,
                )
            result: O365SendResult = await self.o365_service.send_email(
                to=to,
                subject=subject,
                body=body,
                body_type=body_type,
                attachments=attachments,
            )
            return SendEmailResult(
                success=result.success,
                message_id=result.message_id,
                error=result.error,
                provider=EmailProvider.O365,
            )

        if provider == EmailProvider.GMAIL:
            if not status.gmail_connected:
                return SendEmailResult(
                    success=False,
                    error="Gmail is not connected.",
                    provider=EmailProvider.GMAIL,
                )
            result_gmail: GmailSendResult = await self.gmail_service.send_email(
                to=to,
                subject=subject,
                body=body,
                body_type=body_type,
                attachments=attachments,
            )
            return SendEmailResult(
                success=result_gmail.success,
                message_id=result_gmail.message_id,
                error=result_gmail.error,
                provider=EmailProvider.GMAIL,
            )

        return SendEmailResult(
            success=False,
            error=f"Unknown provider: {provider}",
        )

    async def has_connected_provider(self) -> bool:
        """Check if the user has any email provider connected."""
        status = await self.get_provider_status()
        return status.o365_connected or status.gmail_connected
