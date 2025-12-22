"""Repository for CampaignRecipient entity with database operations."""

from datetime import datetime, timezone
from uuid import UUID

from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.email_status import EmailStatus
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class CampaignRecipientsRepository(BaseRepository[CampaignRecipient]):
    """Repository for CampaignRecipient entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, CampaignRecipient)

    async def get_by_campaign_id(
        self,
        campaign_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CampaignRecipient]:
        """Get all recipients for a campaign with pagination."""
        stmt = (
            select(CampaignRecipient)
            .where(CampaignRecipient.campaign_id == campaign_id)
            .options(selectinload(CampaignRecipient.contact))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_campaign_id(self, campaign_id: UUID) -> int:
        """Count recipients for a campaign."""
        stmt = (
            select(func.count())
            .select_from(CampaignRecipient)
            .where(CampaignRecipient.campaign_id == campaign_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_by_status(self, campaign_id: UUID, status: EmailStatus) -> int:
        """Count recipients with a specific email status."""
        stmt = (
            select(func.count())
            .select_from(CampaignRecipient)
            .where(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.email_status == status,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_by_campaign_id(self, campaign_id: UUID) -> int:
        """Delete all recipients for a campaign. Returns count deleted."""
        stmt = delete(CampaignRecipient).where(
            CampaignRecipient.campaign_id == campaign_id
        )
        result = await self.session.execute(stmt)
        # rowcount is available on CursorResult from delete operations
        return getattr(result, "rowcount", 0) or 0

    async def contact_exists_in_campaign(
        self,
        campaign_id: UUID,
        contact_id: UUID,
    ) -> bool:
        """Check if a contact is already a recipient in a campaign."""
        stmt = (
            select(func.count())
            .select_from(CampaignRecipient)
            .where(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.contact_id == contact_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_contact_ids_for_campaign(self, campaign_id: UUID) -> set[UUID]:
        """Get set of contact IDs already in a campaign."""
        stmt = select(CampaignRecipient.contact_id).where(
            CampaignRecipient.campaign_id == campaign_id
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def get_pending_recipients(
        self,
        campaign_id: UUID,
        limit: int,
    ) -> list[CampaignRecipient]:
        """Get pending recipients for a campaign, ordered by ID, with contacts loaded."""
        stmt = (
            select(CampaignRecipient)
            .where(
                CampaignRecipient.campaign_id == campaign_id,
                CampaignRecipient.email_status == EmailStatus.PENDING,
            )
            .options(selectinload(CampaignRecipient.contact))
            .order_by(CampaignRecipient.id)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_email_status(
        self,
        recipient_id: UUID,
        status: EmailStatus,
        sent_at: datetime | None = None,
    ) -> CampaignRecipient:
        """Update the email status of a recipient."""
        recipient = await self.get_by_id(recipient_id)
        if not recipient:
            raise ValueError(f"Recipient {recipient_id} not found")

        recipient.email_status = status
        if sent_at:
            recipient.sent_at = sent_at
        elif status == EmailStatus.SENT:
            recipient.sent_at = datetime.now(timezone.utc)

        await self.session.flush()
        return recipient

    async def mark_as_sent(self, recipient_id: UUID) -> CampaignRecipient:
        """Mark a recipient as sent."""
        return await self.update_email_status(
            recipient_id=recipient_id,
            status=EmailStatus.SENT,
        )

    async def mark_as_failed(self, recipient_id: UUID) -> CampaignRecipient:
        """Mark a recipient as failed."""
        return await self.update_email_status(
            recipient_id=recipient_id,
            status=EmailStatus.FAILED,
        )

    async def get_status_counts(self, campaign_id: UUID) -> dict[EmailStatus, int]:
        """Get counts for each email status in a campaign."""
        stmt = (
            select(
                CampaignRecipient.email_status,
                func.count().label("count"),
            )
            .where(CampaignRecipient.campaign_id == campaign_id)
            .group_by(CampaignRecipient.email_status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return {EmailStatus(row[0]): int(row[1]) for row in rows}
