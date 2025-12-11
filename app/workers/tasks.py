"""TaskIQ tasks for campaign email processing."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from commons.db.controller import MultiTenantController
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config.settings import Settings
from app.core.container import create_container
from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.campaign_send_log_model import CampaignSendLog
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.email_status import EmailStatus
from app.graphql.campaigns.models.send_pace import SendPace
from app.graphql.contacts.models.contact_model import Contact
from app.integrations.gmail.config import GmailSettings
from app.integrations.microsoft_o365.config import O365Settings
from app.workers.broker import broker
from app.workers.services.worker_email_service import WorkerEmailService

# Register Contact model with SQLAlchemy mapper (needed before CampaignRecipient)
_ = Contact

logger = logging.getLogger(__name__)

# Emails per hour for each pace
PACE_LIMITS: dict[SendPace, int] = {
    SendPace.SLOW: 50,
    SendPace.MEDIUM: 200,
    SendPace.FAST: 500,
}

DEFAULT_MAX_EMAILS_PER_DAY = 1000

# Cron schedule: run every minute
CAMPAIGN_PROCESSING_CRON = "* * * * *"


async def get_multitenant_controller(settings: Settings) -> MultiTenantController:
    """
    Create and initialize the multi-tenant controller.

    Args:
        settings: Application settings (injected via DI)

    Returns:
        Initialized MultiTenantController
    """
    controller = MultiTenantController(
        pg_url=settings.pg_url.unicode_string(),
        app_name="Campaign Worker",
        echo=settings.log_level == "DEBUG",
        connect_args={
            "timeout": 5,
            "command_timeout": 90,
        },
        env=settings.environment,
    )
    await controller.load_data_sources()
    return controller


async def process_campaign_batch(
    session: AsyncSession,
    campaign: Campaign,
    user_id: UUID,
    email_service: WorkerEmailService,
) -> dict[str, object]:
    """
    Process a batch of emails for a campaign.

    Args:
        session: Database session
        campaign: Campaign to process
        user_id: User ID (campaign owner)
        email_service: Worker email service for sending

    Returns:
        Dictionary with processing results
    """
    campaign_id = str(campaign.id)

    if campaign.status not in (CampaignStatus.SENDING, CampaignStatus.SCHEDULED):
        logger.info(
            f"Campaign {campaign_id} is not in SENDING status: {campaign.status}"
        )
        return {"status": campaign.status.name, "emails_sent": 0}

    if campaign.status == CampaignStatus.SCHEDULED:
        if campaign.scheduled_at and campaign.scheduled_at > datetime.now(timezone.utc):
            logger.info(
                f"Campaign {campaign_id} scheduled for {campaign.scheduled_at}, not yet due"
            )
            return {
                "status": "SCHEDULED",
                "emails_sent": 0,
                "scheduled_at": str(campaign.scheduled_at),
            }
        campaign.status = CampaignStatus.SENDING
        await session.flush()

    today = datetime.now(timezone.utc).date()
    log_stmt = select(CampaignSendLog).where(
        CampaignSendLog.campaign_id == campaign.id,
        CampaignSendLog.send_date == today,
    )
    log_result = await session.execute(log_stmt)
    send_log = log_result.scalar_one_or_none()

    if not send_log:
        send_log = CampaignSendLog(
            campaign_id=campaign.id,
            send_date=today,
            emails_sent=0,
        )
        session.add(send_log)
        await session.flush()

    max_per_day = campaign.max_emails_per_day or DEFAULT_MAX_EMAILS_PER_DAY
    remaining_today = max(0, max_per_day - send_log.emails_sent)

    if remaining_today == 0:
        logger.info(f"Campaign {campaign_id} reached daily limit of {max_per_day}")
        return {
            "status": "DAILY_LIMIT_REACHED",
            "emails_sent": 0,
            "today_sent": send_log.emails_sent,
            "max_per_day": max_per_day,
        }

    pace = campaign.send_pace or SendPace.MEDIUM
    emails_per_hour = PACE_LIMITS.get(pace, PACE_LIMITS[SendPace.MEDIUM])
    batch_size = max(1, emails_per_hour // 30)
    batch_size = min(batch_size, remaining_today)

    pending_stmt = (
        select(CampaignRecipient)
        .where(
            CampaignRecipient.campaign_id == campaign.id,
            CampaignRecipient.email_status == EmailStatus.PENDING,
        )
        .options(selectinload(CampaignRecipient.contact))
        .limit(batch_size)
    )
    pending_result = await session.execute(pending_stmt)
    recipients = list(pending_result.scalars().all())

    if not recipients:
        campaign.status = CampaignStatus.COMPLETED
        logger.info(f"Campaign {campaign_id} completed - no more pending recipients")
        return {"status": "COMPLETED", "emails_sent": 0}

    sent_count = 0
    failed_count = 0
    errors: list[str] = []

    for recipient in recipients:
        try:
            success = await email_service.send_email_to_recipient(
                session=session,
                campaign=campaign,
                recipient=recipient,
                user_id=user_id,
            )
            if success:
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.exception(f"Error sending to {recipient.contact.email}: {e}")
            recipient.email_status = EmailStatus.FAILED
            failed_count += 1
            errors.append(str(e))

    send_log.emails_sent += sent_count
    send_log.last_sent_at = datetime.now(timezone.utc)

    pending_count_stmt = select(CampaignRecipient).where(
        CampaignRecipient.campaign_id == campaign.id,
        CampaignRecipient.email_status == EmailStatus.PENDING,
    )
    pending_count_result = await session.execute(pending_count_stmt)
    remaining_pending = len(list(pending_count_result.scalars().all()))

    if remaining_pending == 0:
        campaign.status = CampaignStatus.COMPLETED
        logger.info(f"Campaign {campaign_id} completed")

    return {
        "status": campaign.status.name,
        "emails_sent": sent_count,
        "emails_failed": failed_count,
        "remaining_pending": remaining_pending,
        "today_sent": send_log.emails_sent,
        "errors": errors[:5],
    }


@broker.task(schedule=[{"cron": CAMPAIGN_PROCESSING_CRON}])
async def check_and_process_campaigns_task() -> dict[str, object]:
    """
    TaskIQ task: Check for campaigns that need processing and process them.

    This task runs on a cron schedule (every minute) and iterates through
    all tenant databases to find and process active campaigns.

    Uses DI container to resolve settings and services.

    Returns:
        Dictionary with task results including tenants checked and campaigns processed
    """
    start_time = datetime.now(timezone.utc)
    logger.info("=" * 60)
    logger.info(
        f"[{start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}] CAMPAIGN CHECK STARTED"
    )
    logger.info("=" * 60)

    container = create_container()

    async with container.context() as ctx:
        # Resolve dependencies via DI
        settings = await ctx.resolve(Settings)
        o365_settings = await ctx.resolve(O365Settings)
        gmail_settings = await ctx.resolve(GmailSettings)

        # Create services
        email_service = WorkerEmailService(
            o365_settings=o365_settings,
            gmail_settings=gmail_settings,
        )

        controller = await get_multitenant_controller(settings)

        total_campaigns_found = 0
        total_processed: list[str] = []
        tenants_checked = 0
        tenant_names = list(controller.ro_engines.keys())

        logger.info(
            f"[{start_time.strftime('%H:%M:%S')}] Found {len(tenant_names)} tenants to check: {tenant_names}"
        )

        for tenant_name in tenant_names:
            tenants_checked += 1
            tenant_start = datetime.now(timezone.utc)
            logger.info(
                f"[{tenant_start.strftime('%H:%M:%S')}] Checking tenant: {tenant_name}"
            )

            try:
                async with controller.scoped_session(tenant_name) as session:
                    async with session.begin():
                        stmt = select(Campaign).where(
                            Campaign.status.in_(
                                [CampaignStatus.SENDING, CampaignStatus.SCHEDULED]
                            )
                        )
                        result = await session.execute(stmt)
                        campaigns = list(result.scalars().all())

                        if not campaigns:
                            logger.info(
                                f"[{tenant_start.strftime('%H:%M:%S')}]   └── No active campaigns in {tenant_name}"
                            )
                            continue

                        total_campaigns_found += len(campaigns)
                        logger.info(
                            f"[{tenant_start.strftime('%H:%M:%S')}]   └── Found {len(campaigns)} active campaign(s)"
                        )

                        for campaign in campaigns:
                            campaign_time = datetime.now(timezone.utc)
                            if campaign.status == CampaignStatus.SCHEDULED:
                                if (
                                    campaign.scheduled_at
                                    and campaign.scheduled_at
                                    > datetime.now(timezone.utc)
                                ):
                                    logger.info(
                                        f"[{campaign_time.strftime('%H:%M:%S')}]       └── Campaign '{campaign.name}' "
                                        f"scheduled for {campaign.scheduled_at}, skipping"
                                    )
                                    continue

                            logger.info(
                                f"[{campaign_time.strftime('%H:%M:%S')}]       └── Processing campaign: "
                                f"'{campaign.name}' (status: {campaign.status.name})"
                            )

                            try:
                                batch_result = await process_campaign_batch(
                                    session=session,
                                    campaign=campaign,
                                    user_id=campaign.created_by_id,
                                    email_service=email_service,
                                )
                                result_time = datetime.now(timezone.utc)
                                logger.info(
                                    f"[{result_time.strftime('%H:%M:%S')}]           └── Result: "
                                    f"sent={batch_result.get('emails_sent', 0)}, "
                                    f"failed={batch_result.get('emails_failed', 0)}, "
                                    f"remaining={batch_result.get('remaining_pending', 0)}, "
                                    f"status={batch_result.get('status', 'UNKNOWN')}"
                                )
                                total_processed.append(str(campaign.id))
                            except Exception as e:
                                logger.exception(
                                    f"[{campaign_time.strftime('%H:%M:%S')}] Error processing campaign {campaign.id}: {e}"
                                )
            except Exception as e:
                logger.warning(
                    f"[{tenant_start.strftime('%H:%M:%S')}]   └── Error checking tenant {tenant_name}: {type(e).__name__}"
                )

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        logger.info("-" * 60)
        logger.info(
            f"[{end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}] CAMPAIGN CHECK COMPLETED"
        )
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Tenants checked: {tenants_checked}")
        logger.info(f"  Campaigns found: {total_campaigns_found}")
        logger.info(f"  Campaigns processed: {len(total_processed)}")
        logger.info("=" * 60)

        return {
            "tenants_checked": tenants_checked,
            "campaigns_found": total_campaigns_found,
            "campaigns_processed": total_processed,
            "duration_seconds": duration,
        }
