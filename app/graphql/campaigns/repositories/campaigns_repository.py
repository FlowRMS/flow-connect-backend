"""Repository for Campaigns entity with database operations."""

from typing import Any
from uuid import UUID

from commons.db.models import User
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.email_status import EmailStatus
from app.graphql.campaigns.models.recipient_list_type import RecipientListType
from app.graphql.campaigns.strawberry.campaign_landing_page_response import (
    CampaignLandingPageResponse,
)


class CampaignsRepository(BaseRepository[Campaign]):
    """Repository for Campaigns entity."""

    landing_model = CampaignLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Campaign)

    def paginated_stmt(self) -> Select[Any]:
        """Build paginated query for campaigns landing page."""
        recipients_count_subq = (
            select(
                CampaignRecipient.campaign_id,
                func.count(CampaignRecipient.id).label("recipients_count"),
            )
            .group_by(CampaignRecipient.campaign_id)
            .subquery()
        )

        sent_count_subq = (
            select(
                CampaignRecipient.campaign_id,
                func.count(CampaignRecipient.id).label("sent_count"),
            )
            .where(CampaignRecipient.email_status == EmailStatus.SENT)
            .group_by(CampaignRecipient.campaign_id)
            .subquery()
        )

        return (
            select(
                Campaign.id,
                Campaign.created_at,
                func.coalesce(User.full_name, "Unknown").label("created_by"),
                Campaign.name,
                Campaign.status,
                Campaign.recipient_list_type,
                func.coalesce(recipients_count_subq.c.recipients_count, 0).label(
                    "recipients_count"
                ),
                func.coalesce(sent_count_subq.c.sent_count, 0).label("sent_count"),
                Campaign.scheduled_at,
            )
            .select_from(Campaign)
            .options(lazyload("*"))
            .outerjoin(User, User.id == Campaign.created_by_id)
            .outerjoin(
                recipients_count_subq,
                recipients_count_subq.c.campaign_id == Campaign.id,
            )
            .outerjoin(sent_count_subq, sent_count_subq.c.campaign_id == Campaign.id)
        )

    async def get_with_relations(self, campaign_id: UUID) -> Campaign | None:
        """Get campaign with recipients and criteria loaded."""
        stmt = (
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(
                selectinload(Campaign.recipients),
                selectinload(Campaign.criteria),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(self, status: CampaignStatus) -> list[Campaign]:
        """Get all campaigns with a specific status."""
        stmt = select(Campaign).where(Campaign.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_dynamic_campaigns(self) -> list[Campaign]:
        """Get all campaigns with dynamic recipient lists."""
        from app.graphql.campaigns.models.campaign_criteria_model import CampaignCriteria

        stmt = (
            select(Campaign)
            .join(CampaignCriteria, Campaign.id == CampaignCriteria.campaign_id)
            .where(
                Campaign.recipient_list_type == RecipientListType.DYNAMIC,
                CampaignCriteria.is_dynamic == True,  # noqa: E712
            )
            .options(selectinload(Campaign.criteria))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
