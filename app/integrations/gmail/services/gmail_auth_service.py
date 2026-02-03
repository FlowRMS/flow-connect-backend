import base64
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import httpx
from commons.auth import AuthInfo
from commons.db.v6.crm import GmailUserToken

if TYPE_CHECKING:
    from app.graphql.campaigns.services.email_provider_service import EmailAttachment

from app.errors.common_errors import NotFoundError
from app.integrations.gmail.config import GmailSettings
from app.integrations.gmail.constants import (
    GMAIL_API,
    GMAIL_SCOPES,
    GOOGLE_AUTH_ENDPOINT,
    GOOGLE_TOKEN_ENDPOINT,
    GOOGLE_USERINFO_ENDPOINT,
)
from app.integrations.gmail.repositories.gmail_token_repository import (
    GmailTokenRepository,
)


class GmailAuthError(Exception):
    """Raised when Gmail authentication fails."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass
class GmailConnectionStatus:
    """Status of user's Gmail connection."""

    is_connected: bool
    google_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass
class SendEmailResult:
    """Result of sending an email."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@dataclass
class GmailConnectionResult:
    """Result of OAuth connection."""

    success: bool
    google_email: str | None = None
    error: str | None = None


class GmailAuthService:
    """Service for Gmail OAuth flow and email operations."""

    # Buffer time before token expiration to trigger refresh (5 minutes)
    TOKEN_REFRESH_BUFFER_SECONDS = 300

    def __init__(
        self,
        repository: GmailTokenRepository,
        settings: GmailSettings,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.settings = settings
        self.auth_info = auth_info

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate Google OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.
                   If not provided, a random state will be generated.

        Returns:
            Authorization URL to redirect user to
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.settings.gmail_client_id,
            "response_type": "code",
            "redirect_uri": self.settings.gmail_redirect_uri,
            "scope": " ".join(GMAIL_SCOPES),
            "state": state,
            "access_type": "offline",  # Required for refresh token
            "prompt": "consent",  # Force consent to get refresh token
        }

        return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> GmailUserToken:
        """
        Exchange authorization code for access/refresh tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Saved GmailUserToken entity

        Raises:
            GmailAuthError: If token exchange fails
        """
        data = {
            "client_id": self.settings.gmail_client_id,
            "client_secret": self.settings.gmail_client_secret,
            "code": code,
            "redirect_uri": self.settings.gmail_redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)

            if response.status_code != 200:
                error_data = response.json()
                raise GmailAuthError(
                    message=error_data.get(
                        "error_description", "Token exchange failed"
                    ),
                    error_code=error_data.get("error"),
                )

            token_data = response.json()

        # Get user info from Google
        user_info = await self._get_user_info(token_data["access_token"])

        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Save token
        return await self.repository.upsert_token(
            user_id=self.auth_info.flow_user_id,
            google_user_id=user_info["id"],
            google_email=user_info.get("email", ""),
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            expires_at=expires_at,
            scope=token_data.get("scope", " ".join(GMAIL_SCOPES)),
            token_type=token_data.get("token_type", "Bearer"),
        )

    async def _get_user_info(self, access_token: str) -> dict:
        """
        Get user info from Google.

        Args:
            access_token: Valid access token

        Returns:
            User info dictionary

        Raises:
            GmailAuthError: If user info request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_ENDPOINT,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                raise GmailAuthError(
                    message="Failed to get user info from Google",
                    error_code="user_info_failed",
                )

            return response.json()

    async def refresh_token(self, user_id: uuid.UUID) -> GmailUserToken:
        """
        Refresh expired access token using refresh token.

        Args:
            user_id: User whose token to refresh

        Returns:
            Updated GmailUserToken entity

        Raises:
            NotFoundError: If user has no token
            GmailAuthError: If token refresh fails
        """
        token = await self.repository.get_by_user_id(user_id)
        if not token:
            raise NotFoundError(f"No Gmail token found for user {user_id}")

        data = {
            "client_id": self.settings.gmail_client_id,
            "client_secret": self.settings.gmail_client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)

            if response.status_code != 200:
                error_data = response.json()
                # Deactivate token if refresh fails
                _ = await self.repository.deactivate_token(user_id)
                raise GmailAuthError(
                    message=error_data.get("error_description", "Token refresh failed"),
                    error_code=error_data.get("error"),
                )

            token_data = response.json()

        # Calculate new expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Update token (Google doesn't always return a new refresh token)
        return await self.repository.update_tokens(
            token_id=token.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", token.refresh_token),
            expires_at=expires_at,
        )

    async def get_valid_token(self, user_id: uuid.UUID) -> str:
        """
        Get valid access token, refreshing if necessary.

        Args:
            user_id: User whose token to retrieve

        Returns:
            Valid access token string

        Raises:
            NotFoundError: If user has no token
            GmailAuthError: If token refresh fails
        """
        token = await self.repository.get_active_token(user_id)
        if not token:
            raise NotFoundError(f"No active Gmail token found for user {user_id}")

        # Check if token needs refresh (within buffer time of expiration)
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=self.TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now >= refresh_threshold:
            token = await self.refresh_token(user_id)

        await self.repository.update_last_used(token.id)

        return token.access_token

    def _create_message(
        self,
        sender: str,
        to: list[str],
        subject: str,
        body: str,
        body_type: str = "HTML",
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list["EmailAttachment"] | None = None,
    ) -> str:
        """
        Create a base64 encoded email message.

        Args:
            sender: Sender email address
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: Body content type ("HTML" or "Text")
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            attachments: Optional list of file attachments

        Returns:
            Base64 encoded email message
        """
        # Use mixed multipart if we have attachments, otherwise alternative
        if attachments:
            message = MIMEMultipart("mixed")
            # Create a sub-part for the body
            body_part = MIMEMultipart("alternative")
            subtype = "html" if body_type.upper() == "HTML" else "plain"
            body_part.attach(MIMEText(body, subtype))
            message.attach(body_part)
        else:
            message = MIMEMultipart("alternative")
            subtype = "html" if body_type.upper() == "HTML" else "plain"
            message.attach(MIMEText(body, subtype))

        message["From"] = sender
        message["To"] = ", ".join(to)
        message["Subject"] = subject

        if cc:
            message["Cc"] = ", ".join(cc)
        if bcc:
            message["Bcc"] = ", ".join(bcc)

        # Add attachments
        if attachments:
            for att in attachments:
                maintype, subtype = att.content_type.split("/", 1)
                part = MIMEBase(maintype, subtype)
                part.set_payload(att.content)
                encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=att.filename,
                )
                message.attach(part)

        # Encode to base64
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return raw

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        body_type: str = "HTML",
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list["EmailAttachment"] | None = None,
    ) -> SendEmailResult:
        """
        Send email on behalf of user via Gmail API.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: Body content type ("HTML" or "Text")
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            attachments: Optional list of file attachments

        Returns:
            SendEmailResult with success status and optional message_id or error
        """
        try:
            access_token = await self.get_valid_token(self.auth_info.flow_user_id)
        except (NotFoundError, GmailAuthError) as e:
            return SendEmailResult(success=False, error=str(e))

        # Get sender email from stored token
        token = await self.repository.get_by_user_id(self.auth_info.flow_user_id)
        if not token:
            return SendEmailResult(success=False, error="No Gmail token found")

        sender = token.google_email

        # Create the message
        raw_message = self._create_message(
            sender=sender,
            to=to,
            subject=subject,
            body=body,
            body_type=body_type,
            cc=cc,
            bcc=bcc,
            attachments=attachments,
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GMAIL_API}/users/me/messages/send",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"raw": raw_message},
            )

            if response.status_code == 200:
                result = response.json()
                return SendEmailResult(
                    success=True,
                    message_id=result.get("id"),
                )

            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", "Failed to send email"
            )
            return SendEmailResult(success=False, error=error_message)

    async def revoke_access(self) -> bool:
        """
        Revoke/deactivate current user's Gmail integration.

        Returns:
            True if token was deactivated, False if no token found
        """
        return await self.repository.deactivate_token(self.auth_info.flow_user_id)

    async def get_connection_status(self) -> GmailConnectionStatus:
        """
        Check current user's Gmail connection status.

        Returns:
            GmailConnectionStatus with connection details
        """
        token = await self.repository.get_by_user_id(self.auth_info.flow_user_id)

        if not token or not token.is_active:
            return GmailConnectionStatus(is_connected=False)

        return GmailConnectionStatus(
            is_connected=True,
            google_email=token.google_email,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
        )
