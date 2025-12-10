"""Repository for CampaignRecipient entity with database operations."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.email_status import EmailStatus


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
        return result.rowcount

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
