import secrets
import uuid
from datetime import datetime, timedelta, timezone
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
from app.integrations.gmail.services.gmail_message_builder import create_message
from app.integrations.gmail.services.gmail_types import (
    GmailAuthError,
    GmailConnectionResult,
    GmailConnectionStatus,
    SendEmailResult,
)

# Re-export for backward compatibility
__all__ = [
    "GmailAuthError",
    "GmailAuthService",
    "GmailConnectionResult",
    "GmailConnectionStatus",
    "SendEmailResult",
]


class GmailAuthService:
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

        If state is not provided, a random CSRF token will be generated.
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

        Checks the token expiration against a buffer window, and refreshes
        the token proactively if it's about to expire.
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
        raw_message = create_message(
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
        return await self.repository.deactivate_token(self.auth_info.flow_user_id)

    async def get_connection_status(self) -> GmailConnectionStatus:
        token = await self.repository.get_by_user_id(self.auth_info.flow_user_id)

        if not token or not token.is_active:
            return GmailConnectionStatus(is_connected=False)

        return GmailConnectionStatus(
            is_connected=True,
            google_email=token.google_email,
            expires_at=token.expires_at,
            last_used_at=token.last_used_at,
        )
