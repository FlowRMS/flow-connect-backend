"""Email strategy for Gmail."""

import base64
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import UUID

import httpx
from commons.db.v6.crm import GmailUserToken
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.gmail.config import GmailSettings
from app.integrations.gmail.constants import GMAIL_API

from .base import (
    TOKEN_REFRESH_BUFFER_SECONDS,
    EmailStrategy,
    WorkerSendEmailResult,
)


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
            GmailUserToken.is_active.is_(True),
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
