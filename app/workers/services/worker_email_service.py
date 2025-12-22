"""Worker email service for sending campaign emails without AuthInfo context."""

from datetime import datetime, timezone
from uuid import UUID

from commons.db.v6.crm.campaigns.campaign_model import Campaign
from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.email_status import EmailStatus
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.gmail.config import GmailSettings
from app.integrations.microsoft_o365.config import O365Settings

from .strategies import (
    EmailStrategy,
    GmailEmailStrategy,
    O365EmailStrategy,
)


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
