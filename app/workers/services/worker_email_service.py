"""Worker email service for sending campaign emails without AuthInfo context."""

import base64
import logging
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


class WorkerEmailService:
    """
    Service for sending emails in worker context without AuthInfo.

    This service is designed for background workers that process campaigns
    across all tenants and users. It handles token refresh and email sending
    for both O365 and Gmail providers.
    """

    def __init__(
        self,
        o365_settings: O365Settings,
        gmail_settings: GmailSettings,
    ) -> None:
        super().__init__()
        self.o365_settings = o365_settings
        self.gmail_settings = gmail_settings

    async def refresh_o365_token_if_needed(
        self,
        session: AsyncSession,
        token: O365UserToken,
    ) -> str | None:
        """
        Refresh O365 token if expired or about to expire.

        Args:
            session: Database session for updating token
            token: O365 token to potentially refresh

        Returns:
            Valid access token or None if refresh failed
        """
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now < refresh_threshold:
            return token.access_token

        logger.info(f"Refreshing O365 token for user {token.user_id}")

        data = {
            "client_id": self.o365_settings.o365_client_id,
            "client_secret": self.o365_settings.o365_client_secret,
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

    async def refresh_gmail_token_if_needed(
        self,
        session: AsyncSession,
        token: GmailUserToken,
    ) -> str | None:
        """
        Refresh Gmail token if expired or about to expire.

        Args:
            session: Database session for updating token
            token: Gmail token to potentially refresh

        Returns:
            Valid access token or None if refresh failed
        """
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now < refresh_threshold:
            return token.access_token

        logger.info(f"Refreshing Gmail token for user {token.user_id}")

        data = {
            "client_id": self.gmail_settings.gmail_client_id,
            "client_secret": self.gmail_settings.gmail_client_secret,
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

    async def send_via_o365(
        self,
        access_token: str,
        to: str,
        subject: str,
        body: str,
    ) -> WorkerSendEmailResult:
        """
        Send email via Microsoft Graph API.

        Args:
            access_token: Valid O365 access token
            to: Recipient email address
            subject: Email subject
            body: HTML email body

        Returns:
            WorkerSendEmailResult with success status
        """
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

    async def send_via_gmail(
        self,
        access_token: str,
        sender: str,
        to: str,
        subject: str,
        body: str,
    ) -> WorkerSendEmailResult:
        """
        Send email via Gmail API.

        Args:
            access_token: Valid Gmail access token
            sender: Sender email address
            to: Recipient email address
            subject: Email subject
            body: HTML email body

        Returns:
            WorkerSendEmailResult with success status
        """
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

        # Try O365 first
        o365_stmt = select(O365UserToken).where(
            O365UserToken.user_id == user_id,
            O365UserToken.is_active == True,  # noqa: E712
        )
        o365_result = await session.execute(o365_stmt)
        o365_token = o365_result.scalar_one_or_none()

        logger.info(
            f"O365 token lookup for user {user_id}: {'found' if o365_token else 'not found'}"
        )

        if o365_token:
            access_token = await self.refresh_o365_token_if_needed(session, o365_token)
            if not access_token:
                logger.warning(
                    f"O365 token expired and refresh failed for user {user_id}"
                )
            else:
                result = await self.send_via_o365(
                    access_token=access_token,
                    to=contact.email,
                    subject=subject,
                    body=body,
                )
                if result.success:
                    recipient.email_status = EmailStatus.SENT
                    recipient.sent_at = datetime.now(timezone.utc)
                    return True
                logger.error(f"O365 send failed: {result.error}")
                recipient.email_status = EmailStatus.FAILED
                return False

        # Try Gmail
        gmail_stmt = select(GmailUserToken).where(
            GmailUserToken.user_id == user_id,
            GmailUserToken.is_active == True,  # noqa: E712
        )
        gmail_result = await session.execute(gmail_stmt)
        gmail_token = gmail_result.scalar_one_or_none()

        logger.info(
            f"Gmail token lookup for user {user_id}: {'found' if gmail_token else 'not found'}"
        )

        if gmail_token:
            access_token = await self.refresh_gmail_token_if_needed(
                session, gmail_token
            )
            if not access_token:
                logger.warning(
                    f"Gmail token expired and refresh failed for user {user_id}"
                )
            else:
                result = await self.send_via_gmail(
                    access_token=access_token,
                    sender=gmail_token.google_email,
                    to=contact.email,
                    subject=subject,
                    body=body,
                )
                if result.success:
                    recipient.email_status = EmailStatus.SENT
                    recipient.sent_at = datetime.now(timezone.utc)
                    return True
                logger.error(f"Gmail send failed: {result.error}")
                recipient.email_status = EmailStatus.FAILED
                return False

        logger.warning(f"No email provider connected for user {user_id}")
        recipient.email_status = EmailStatus.FAILED
        return False
