"""Email strategy for Microsoft Office 365."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from commons.db.v6.crm import O365UserToken
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.microsoft_o365.config import O365Settings
from app.integrations.microsoft_o365.constants import (
    MICROSOFT_GRAPH_API,
    O365_SCOPES,
    TOKEN_ENDPOINT,
)

from .base import (
    TOKEN_REFRESH_BUFFER_SECONDS,
    EmailStrategy,
    WorkerSendEmailResult,
)


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
            O365UserToken.user_id == user_id, O365UserToken.is_active.is_(True)
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
