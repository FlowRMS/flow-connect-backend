"""Repository for CampaignSendLog entity with database operations."""

from datetime import date, datetime, timezone
from uuid import UUID

from commons.db.v6.crm.campaigns.campaign_send_log_model import CampaignSendLog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class CampaignSendLogRepository(BaseRepository[CampaignSendLog]):
    """Repository for CampaignSendLog entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, CampaignSendLog)

    async def get_today_log(self, campaign_id: UUID) -> CampaignSendLog | None:
        """Get today's send log for a campaign."""
        today = date.today()
        stmt = select(CampaignSendLog).where(
            CampaignSendLog.campaign_id == campaign_id,
            CampaignSendLog.send_date == today,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_today_log(self, campaign_id: UUID) -> CampaignSendLog:
        """Get or create today's send log for a campaign."""
        log = await self.get_today_log(campaign_id)
        if log:
            return log

        log = CampaignSendLog(
            campaign_id=campaign_id,
            send_date=date.today(),
            emails_sent=0,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def increment_sent_count(
        self,
        campaign_id: UUID,
        count: int = 1,
    ) -> CampaignSendLog:
        """Increment the sent count for today's log."""
        log = await self.get_or_create_today_log(campaign_id)
        log.emails_sent += count
        log.last_sent_at = datetime.now(timezone.utc)
        await self.session.flush()
        return log

    async def get_today_sent_count(self, campaign_id: UUID) -> int:
        """Get the number of emails sent today for a campaign."""
        log = await self.get_today_log(campaign_id)
        return log.emails_sent if log else 0

    async def get_log_by_date(
        self,
        campaign_id: UUID,
        send_date: date,
    ) -> CampaignSendLog | None:
        """Get send log for a specific date."""
        stmt = select(CampaignSendLog).where(
            CampaignSendLog.campaign_id == campaign_id,
            CampaignSendLog.send_date == send_date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_logs_for_campaign(
        self,
        campaign_id: UUID,
        limit: int = 30,
    ) -> list[CampaignSendLog]:
        """Get recent send logs for a campaign, ordered by date descending."""
        stmt = (
            select(CampaignSendLog)
            .where(CampaignSendLog.campaign_id == campaign_id)
            .order_by(CampaignSendLog.send_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
