"""Worker email service for sending campaign emails without AuthInfo context."""

import base64
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.email_status import EmailStatus
from app.integrations.gmail.config import GmailSettings
from app.integrations.gmail.constants import GMAIL_API
from app.integrations.gmail.models.gmail_user_token import GmailUserToken
from app.integrations.microsoft_o365.config import O365Settings
from app.integrations.microsoft_o365.constants import (
    MICROSOFT_GRAPH_API,
    O365_SCOPES,
    TOKEN_ENDPOINT,
)
from app.integrations.microsoft_o365.models.o365_user_token import O365UserToken

logger = logging.getLogger(__name__)

# Buffer time before token expiration to trigger refresh (5 minutes)
TOKEN_REFRESH_BUFFER_SECONDS = 300


@dataclass
class WorkerSendEmailResult:
    """Result of sending an email in worker context."""

    success: bool
    error: str | None = None


class EmailStrategy(ABC):
    """Abstract base class for email sending strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy name for logging."""
        ...

    @abstractmethod
    async def get_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> object | None:
        """
        Get the user's token for this email provider.

        Args:
            session: Database session
            user_id: User ID to look up token for

        Returns:
            Token object if available and active, None otherwise
        """
        ...

    @abstractmethod
    async def refresh_token_if_needed(
        self,
        session: AsyncSession,
        token: object,
    ) -> str | None:
        """
        Refresh token if expired or about to expire.

        Args:
            session: Database session for updating token
            token: Token to potentially refresh

        Returns:
            Valid access token or None if refresh failed
        """
        ...

    @abstractmethod
    async def send(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str,
        sender: str | None = None,
    ) -> WorkerSendEmailResult:
        """
        Send an email using this provider.

        Args:
            access_token: Valid access token
            to: Recipient email address
            subject: Email subject
            body: HTML email body
            sender: Sender email (required for some providers)

        Returns:
            WorkerSendEmailResult with success status
        """
        ...

    async def is_available(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> bool:
        """
        Check if this strategy is available for the user.

        Args:
            session: Database session
            user_id: User ID to check availability for

        Returns:
            True if strategy is available, False otherwise
        """
        token = await self.get_token(session, user_id)
        return token is not None


class O365EmailStrategy(EmailStrategy):
    """Email strategy for Microsoft Office 365."""

    def __init__(self, settings: O365Settings) -> None:
        super().__init__()
        self.settings = settings

    @property
    def name(self) -> str:
        return "O365"

    async def get_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> O365UserToken | None:
        stmt = select(O365UserToken).where(
            O365UserToken.user_id == user_id,
            O365UserToken.is_active == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def refresh_token_if_needed(
        self,
        session: AsyncSession,
        token: O365UserToken,
    ) -> str | None:
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now < refresh_threshold:
            return token.access_token

        logger.info(f"Refreshing O365 token for user {token.user_id}")

        data = {
            "client_id": self.settings.o365_client_id,
            "client_secret": self.settings.o365_client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(O365_SCOPES),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(TOKEN_ENDPOINT, data=data, timeout=30.0)

                if response.status_code != 200:
                    logger.error(f"O365 token refresh failed: {response.text}")
                    token.is_active = False
                    return None

                token_data = response.json()

            expires_in = token_data.get("expires_in", 3600)
            token.access_token = token_data["access_token"]
            token.refresh_token = token_data.get("refresh_token", token.refresh_token)
            token.expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in
            )
            await session.flush()

            return token.access_token
        except Exception as e:
            logger.exception(f"Error refreshing O365 token: {e}")
            return None

    async def send(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str,
        sender: str | None = None,
    ) -> WorkerSendEmailResult:
        message = {
            "message": {
                "subject": subject,
                "body": {"contentType": "HTML", "content": body},
                "toRecipients": [{"emailAddress": {"address": to}}],
            },
            "saveToSentItems": "true",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{MICROSOFT_GRAPH_API}/me/sendMail",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=message,
                    timeout=30.0,
                )

                if response.status_code == 202:
                    return WorkerSendEmailResult(success=True)

                return WorkerSendEmailResult(
                    success=False,
                    error=f"O365 API error: {response.status_code} - {response.text}",
                )
        except Exception as e:
            return WorkerSendEmailResult(success=False, error=str(e))


class GmailEmailStrategy(EmailStrategy):
    """Email strategy for Gmail."""

    def __init__(self, settings: GmailSettings) -> None:
        super().__init__()
        self.settings = settings

    @property
    def name(self) -> str:
        return "Gmail"

    async def get_token(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> GmailUserToken | None:
        stmt = select(GmailUserToken).where(
            GmailUserToken.user_id == user_id,
            GmailUserToken.is_active == True,  # noqa: E712
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def refresh_token_if_needed(
        self,
        session: AsyncSession,
        token: GmailUserToken,
    ) -> str | None:
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now < refresh_threshold:
            return token.access_token

        logger.info(f"Refreshing Gmail token for user {token.user_id}")

        data = {
            "client_id": self.settings.gmail_client_id,
            "client_secret": self.settings.gmail_client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data=data,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"Gmail token refresh failed: {response.text}")
                    token.is_active = False
                    return None

                token_data = response.json()

            expires_in = token_data.get("expires_in", 3600)
            token.access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                token.refresh_token = token_data["refresh_token"]
            token.expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in
            )
            await session.flush()

            return token.access_token
        except Exception as e:
            logger.exception(f"Error refreshing Gmail token: {e}")
            return None

    async def send(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str,
        sender: str | None = None,
    ) -> WorkerSendEmailResult:
        if not sender:
            return WorkerSendEmailResult(
                success=False, error="Gmail requires sender email"
            )

        message = MIMEMultipart("alternative")
        message["From"] = sender
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{GMAIL_API}/users/me/messages/send",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json={"raw": raw},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return WorkerSendEmailResult(success=True)

                return WorkerSendEmailResult(
                    success=False,
                    error=f"Gmail API error: {response.status_code} - {response.text}",
                )
        except Exception as e:
            return WorkerSendEmailResult(success=False, error=str(e))


class WorkerEmailService:
    """
    Service for sending emails in worker context without AuthInfo.

    This service is designed for background workers that process campaigns
    across all tenants and users. It uses registered email strategies
    (O365, Gmail) with automatic fallback.
    """

    def __init__(
        self,
        o365_settings: O365Settings,
        gmail_settings: GmailSettings,
    ) -> None:
        super().__init__()
        # Register strategies in priority order (O365 first, Gmail second)
        self._strategies: list[EmailStrategy] = [
            O365EmailStrategy(o365_settings),
            GmailEmailStrategy(gmail_settings),
        ]

    @property
    def strategies(self) -> list[EmailStrategy]:
        """Return the list of registered email strategies."""
        return self._strategies

    async def get_strategy(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> tuple[EmailStrategy, object] | None:
        """
        Get the first available email strategy for the user.

        Tries O365 first, then falls back to Gmail.

        Args:
            session: Database session
            user_id: User ID to find strategy for

        Returns:
            Tuple of (strategy, token) if available, None otherwise
        """
        for strategy in self._strategies:
            token = await strategy.get_token(session, user_id)
            if token:
                logger.info(f"{strategy.name} token lookup for user {user_id}: found")
                return (strategy, token)
            logger.info(f"{strategy.name} token lookup for user {user_id}: not found")
        return None

    async def send_email_to_recipient(
        self,
        session: AsyncSession,
        campaign: Campaign,
        recipient: CampaignRecipient,
        user_id: UUID,
    ) -> bool:
        """
        Send email to a single recipient using the user's connected email provider.

        Args:
            session: Database session
            campaign: Campaign being processed
            recipient: Recipient to send to (must have contact loaded)
            user_id: User ID whose email provider to use

        Returns:
            True if email was sent successfully, False otherwise
        """
        contact = recipient.contact
        if not contact.email:
            recipient.email_status = EmailStatus.FAILED
            return False

        subject = campaign.email_subject or "Campaign Email"
        body = recipient.personalized_content or campaign.email_body or ""

        strategy_result = await self.get_strategy(session, user_id)
        if not strategy_result:
            logger.warning(f"No email provider connected for user {user_id}")
            recipient.email_status = EmailStatus.FAILED
            return False

        strategy, token = strategy_result

        access_token = await strategy.refresh_token_if_needed(session, token)
        if not access_token:
            logger.warning(
                f"{strategy.name} token expired and refresh failed for user {user_id}"
            )
            recipient.email_status = EmailStatus.FAILED
            return False

        # Get sender email for Gmail (from token)
        sender = getattr(token, "google_email", None)

        result = await strategy.send(
            access_token=access_token,
            to=contact.email,
            subject=subject,
            body=body,
            sender=sender,
        )

        if result.success:
            recipient.email_status = EmailStatus.SENT
            recipient.sent_at = datetime.now(timezone.utc)
            return True

        logger.error(f"{strategy.name} send failed: {result.error}")
        recipient.email_status = EmailStatus.FAILED
        return False
