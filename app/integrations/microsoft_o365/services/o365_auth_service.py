"""Service for Microsoft O365 OAuth authentication and email operations."""

import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from commons.auth import AuthInfo
from commons.db.v6.crm import O365UserToken

from app.errors.common_errors import NotFoundError
from app.integrations.microsoft_o365.config import O365Settings
from app.integrations.microsoft_o365.constants import (
    AUTHORIZE_ENDPOINT,
    MICROSOFT_GRAPH_API,
    O365_SCOPES,
    TOKEN_ENDPOINT,
)
from app.integrations.microsoft_o365.repositories.o365_token_repository import (
    O365TokenRepository,
)


class O365AuthError(Exception):
    """Raised when O365 authentication fails."""

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code


@dataclass
class O365ConnectionStatus:
    """Status of user's O365 connection."""

    is_connected: bool
    microsoft_email: str | None = None
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass
class SendEmailResult:
    """Result of sending an email."""

    success: bool
    message_id: str | None = None
    error: str | None = None


@dataclass
class O365ConnectionResult:
    """Result of OAuth connection."""

    success: bool
    microsoft_email: str | None = None
    error: str | None = None


class O365AuthService:
    """Service for Microsoft O365 OAuth flow and email operations."""

    # Buffer time before token expiration to trigger refresh (5 minutes)
    TOKEN_REFRESH_BUFFER_SECONDS = 300

    def __init__(
        self,
        repository: O365TokenRepository,
        settings: O365Settings,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.settings = settings
        self.auth_info = auth_info

    def get_authorization_url(self, state: str | None = None) -> str:
        """
        Generate Microsoft OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.
                   If not provided, a random state will be generated.

        Returns:
            Authorization URL to redirect user to
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.settings.o365_client_id,
            "response_type": "code",
            "redirect_uri": self.settings.o365_redirect_uri,
            "response_mode": "query",
            "scope": " ".join(O365_SCOPES),
            "state": state,
        }

        return f"{AUTHORIZE_ENDPOINT}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> O365UserToken:
        """
        Exchange authorization code for access/refresh tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Saved O365UserToken entity

        Raises:
            O365AuthError: If token exchange fails
        """
        data = {
            "client_id": self.settings.o365_client_id,
            "client_secret": self.settings.o365_client_secret,
            "code": code,
            "redirect_uri": self.settings.o365_redirect_uri,
            "grant_type": "authorization_code",
            "scope": " ".join(O365_SCOPES),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(TOKEN_ENDPOINT, data=data)

            if response.status_code != 200:
                error_data = response.json()
                raise O365AuthError(
                    message=error_data.get(
                        "error_description", "Token exchange failed"
                    ),
                    error_code=error_data.get("error"),
                )

            token_data = response.json()

        print(f"Token data: {token_data}")

        # Get user info from Microsoft Graph
        user_info = await self._get_user_info(token_data["access_token"])

        # Calculate expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Save token
        return await self.repository.upsert_token(
            user_id=self.auth_info.flow_user_id,
            microsoft_user_id=user_info["id"],
            microsoft_email=user_info.get("mail")
            or user_info.get("userPrincipalName", ""),
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=expires_at,
            scope=token_data.get("scope", " ".join(O365_SCOPES)),
            token_type=token_data.get("token_type", "Bearer"),
        )

    async def _get_user_info(self, access_token: str) -> dict:
        """
        Get user info from Microsoft Graph API.

        Args:
            access_token: Valid access token

        Returns:
            User info dictionary

        Raises:
            O365AuthError: If user info request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MICROSOFT_GRAPH_API}/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                raise O365AuthError(
                    message="Failed to get user info from Microsoft Graph",
                    error_code="user_info_failed",
                )

            return response.json()

    async def refresh_token(self, user_id: uuid.UUID) -> O365UserToken:
        """
        Refresh expired access token using refresh token.

        Args:
            user_id: User whose token to refresh

        Returns:
            Updated O365UserToken entity

        Raises:
            NotFoundError: If user has no token
            O365AuthError: If token refresh fails
        """
        token = await self.repository.get_by_user_id(user_id)
        if not token:
            raise NotFoundError(f"No O365 token found for user {user_id}")

        data = {
            "client_id": self.settings.o365_client_id,
            "client_secret": self.settings.o365_client_secret,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(O365_SCOPES),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(TOKEN_ENDPOINT, data=data)

            if response.status_code != 200:
                error_data = response.json()
                _ = await self.repository.deactivate_token(user_id)
                raise O365AuthError(
                    message=error_data.get("error_description", "Token refresh failed"),
                    error_code=error_data.get("error"),
                )

            token_data = response.json()

        # Calculate new expiration time
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Update token
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
            O365AuthError: If token refresh fails
        """
        token = await self.repository.get_active_token(user_id)
        if not token:
            raise NotFoundError(f"No active O365 token found for user {user_id}")

        # Check if token needs refresh (within buffer time of expiration)
        now = datetime.now(timezone.utc)
        refresh_threshold = token.expires_at - timedelta(
            seconds=self.TOKEN_REFRESH_BUFFER_SECONDS
        )

        if now >= refresh_threshold:
            token = await self.refresh_token(user_id)

        await self.repository.update_last_used(token.id)

        return token.access_token

    async def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        body_type: str = "HTML",
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        save_to_sent_items: bool = True,
    ) -> SendEmailResult:
        """
        Send email on behalf of user via Microsoft Graph API.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            body_type: Body content type ("HTML" or "Text")
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            save_to_sent_items: Whether to save to sent items folder

        Returns:
            SendEmailResult with success status and optional message_id or error
        """
        try:
            access_token = await self.get_valid_token(self.auth_info.flow_user_id)
        except (NotFoundError, O365AuthError) as e:
            return SendEmailResult(success=False, error=str(e))

        # Build email message
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": body_type,
                    "content": body,
                },
                "toRecipients": [{"emailAddress": {"address": email}} for email in to],
            },
            "saveToSentItems": str(save_to_sent_items).lower(),
        }

        if cc:
            message["message"]["ccRecipients"] = [
                {"emailAddress": {"address": email}} for email in cc
            ]

        if bcc:
            message["message"]["bccRecipients"] = [
                {"emailAddress": {"address": email}} for email in bcc
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MICROSOFT_GRAPH_API}/me/sendMail",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=message,
            )

            if response.status_code == 202:
                return SendEmailResult(success=True)

            error_data = response.json()
            error_message = error_data.get("error", {}).get(
                "message", "Failed to send email"
            )
            return SendEmailResult(success=False, error=error_message)

    async def revoke_access(self) -> bool:
        """
        Revoke/deactivate current user's O365 integration.

        Returns:
            True if token was deactivated, False if no token found
        """
        return await self.repository.deactivate_token(self.auth_info.flow_user_id)

    async def get_connection_status(self) -> O365ConnectionStatus:
        """
        Check current user's O365 connection status.

        Returns:
            O365ConnectionStatus with connection details
        """
        token = await self.repository.get_by_user_id(self.auth_info.flow_user_id)

        if not token or not token.is_active:
            return O365ConnectionStatus(is_connected=False)

        return O365ConnectionStatus(
            is_connected=True,
            microsoft_email=token.microsoft_email,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
        )
