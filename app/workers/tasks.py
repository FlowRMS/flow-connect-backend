"""TaskIQ tasks for campaign email processing."""

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.controller import MultiTenantController
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings
from app.workers.broker import broker

if TYPE_CHECKING:
    from app.integrations.gmail.models.gmail_user_token import GmailUserToken
    from app.integrations.microsoft_o365.models.o365_user_token import O365UserToken

# Import Contact model to register it with SQLAlchemy before CampaignRecipient
from app.graphql.contacts.models.contact_model import Contact

_ = Contact  # Register model with SQLAlchemy mapper

from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.email_status import EmailStatus
from app.graphql.campaigns.models.send_pace import SendPace

logger = logging.getLogger(__name__)

# Emails per hour for each pace
PACE_LIMITS: dict[SendPace, int] = {
    SendPace.SLOW: 50,
    SendPace.MEDIUM: 200,
    SendPace.FAST: 500,
}

DEFAULT_MAX_EMAILS_PER_DAY = 1000


async def get_multitenant_controller() -> MultiTenantController:
    """Create and initialize the multi-tenant controller."""
    settings = get_settings(Settings)
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


async def _refresh_o365_token_if_needed(
    session: AsyncSession,
    token: "O365UserToken",
) -> str | None:
    """Refresh O365 token if expired or about to expire. Returns valid access token or None."""
    import httpx

    from app.core.config.base_settings import get_settings
    from app.integrations.microsoft_o365.config import O365Settings
    from app.integrations.microsoft_o365.constants import O365_SCOPES, TOKEN_ENDPOINT

    now = datetime.now(timezone.utc)
    refresh_threshold = token.expires_at - timedelta(seconds=300)

    if now < refresh_threshold:
        return token.access_token

    logger.info(f"Refreshing O365 token for user {token.user_id}")
    settings = get_settings(O365Settings)

    data = {
        "client_id": settings.o365_client_id,
        "client_secret": settings.o365_client_secret,
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
        token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        await session.flush()

        return token.access_token
    except Exception as e:
        logger.exception(f"Error refreshing O365 token: {e}")
        return None


async def _refresh_gmail_token_if_needed(
    session: AsyncSession,
    token: "GmailUserToken",
) -> str | None:
    """Refresh Gmail token if expired or about to expire. Returns valid access token or None."""
    import httpx

    from app.core.config.base_settings import get_settings
    from app.integrations.gmail.config import GmailSettings

    now = datetime.now(timezone.utc)
    refresh_threshold = token.expires_at - timedelta(seconds=300)

    if now < refresh_threshold:
        return token.access_token

    logger.info(f"Refreshing Gmail token for user {token.user_id}")
    settings = get_settings(GmailSettings)

    data = {
        "client_id": settings.gmail_client_id,
        "client_secret": settings.gmail_client_secret,
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
        token.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        await session.flush()

        return token.access_token
    except Exception as e:
        logger.exception(f"Error refreshing Gmail token: {e}")
        return None


async def _send_via_o365(
    access_token: str,
    to: str,
    subject: str,
    body: str,
) -> bool:
    """Send email via Microsoft Graph API."""
    import httpx

    message = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}],
        },
        "saveToSentItems": "true",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=message,
            timeout=30.0,
        )
        return response.status_code == 202


async def _send_via_gmail(
    access_token: str,
    sender: str,
    to: str,
    subject: str,
    body: str,
) -> bool:
    """Send email via Gmail API."""
    import base64
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    import httpx

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={"raw": raw},
            timeout=30.0,
        )
        return response.status_code == 200


async def _send_email_to_recipient(
    session: AsyncSession,
    campaign: Campaign,
    recipient: CampaignRecipient,
    user_id: str,
) -> bool:
    """Send email to a single recipient using the user's connected email provider."""
    from app.integrations.gmail.models.gmail_user_token import GmailUserToken
    from app.integrations.microsoft_o365.models.o365_user_token import O365UserToken

    contact = recipient.contact
    if not contact.email:
        recipient.email_status = EmailStatus.FAILED
        return False

    subject = campaign.email_subject or "Campaign Email"
    body = recipient.personalized_content or campaign.email_body or ""

    user_uuid = UUID(user_id)

    # Try O365 first
    o365_stmt = select(O365UserToken).where(
        O365UserToken.user_id == user_uuid,
        O365UserToken.is_active == True,  # noqa: E712
    )
    o365_result = await session.execute(o365_stmt)
    o365_token = o365_result.scalar_one_or_none()

    if o365_token:
        access_token = await _refresh_o365_token_if_needed(session, o365_token)
        if not access_token:
            logger.warning(f"O365 token expired and refresh failed for user {user_id}")
        else:
            success = await _send_via_o365(
                access_token=access_token,
                to=contact.email,
                subject=subject,
                body=body,
            )
            if success:
                recipient.email_status = EmailStatus.SENT
                recipient.sent_at = datetime.now(timezone.utc)
                return True
            recipient.email_status = EmailStatus.FAILED
            return False

    # Try Gmail
    gmail_stmt = select(GmailUserToken).where(
        GmailUserToken.user_id == user_uuid,
        GmailUserToken.is_active == True,  # noqa: E712
    )
    gmail_result = await session.execute(gmail_stmt)
    gmail_token = gmail_result.scalar_one_or_none()

    if gmail_token:
        access_token = await _refresh_gmail_token_if_needed(session, gmail_token)
        if not access_token:
            logger.warning(f"Gmail token expired and refresh failed for user {user_id}")
        else:
            success = await _send_via_gmail(
                access_token=access_token,
                sender=gmail_token.google_email,
                to=contact.email,
                subject=subject,
                body=body,
            )
            if success:
                recipient.email_status = EmailStatus.SENT
                recipient.sent_at = datetime.now(timezone.utc)
                return True
            recipient.email_status = EmailStatus.FAILED
            return False

    logger.warning(f"No email provider connected for user {user_id}")
    recipient.email_status = EmailStatus.FAILED
    return False


async def _process_campaign_batch(
    session: AsyncSession,
    campaign: Campaign,
    user_id: str,
) -> dict[str, object]:
    """Process a batch of emails for a campaign."""
    from app.graphql.campaigns.models.campaign_send_log_model import CampaignSendLog

    campaign_id = str(campaign.id)

    if campaign.status not in (CampaignStatus.SENDING, CampaignStatus.SCHEDULED):
        logger.info(f"Campaign {campaign_id} is not in SENDING status: {campaign.status}")
        return {"status": campaign.status.name, "emails_sent": 0}

    if campaign.status == CampaignStatus.SCHEDULED:
        if campaign.scheduled_at and campaign.scheduled_at > datetime.now(timezone.utc):
            logger.info(f"Campaign {campaign_id} scheduled for {campaign.scheduled_at}, not yet due")
            return {"status": "SCHEDULED", "emails_sent": 0, "scheduled_at": str(campaign.scheduled_at)}
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
            success = await _send_email_to_recipient(
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


@broker.task
async def check_and_process_campaigns_task() -> dict[str, object]:
    """
    TaskIQ task: Check for campaigns that need processing and process them.
    Iterates through all tenant databases.
    """
    controller = await get_multitenant_controller()

    total_campaigns_found = 0
    total_processed: list[str] = []
    tenants_checked = 0

    for tenant_name in controller.ro_engines:
        tenants_checked += 1
        logger.debug(f"Checking tenant: {tenant_name}")

        try:
            async with controller.scoped_session(tenant_name) as session:
                async with session.begin():
                    stmt = select(Campaign).where(
                        Campaign.status.in_([CampaignStatus.SENDING, CampaignStatus.SCHEDULED])
                    )
                    result = await session.execute(stmt)
                    campaigns = list(result.scalars().all())

                    if not campaigns:
                        continue

                    total_campaigns_found += len(campaigns)

                    for campaign in campaigns:
                        if campaign.status == CampaignStatus.SCHEDULED:
                            if campaign.scheduled_at and campaign.scheduled_at > datetime.now(timezone.utc):
                                continue

                        try:
                            batch_result = await _process_campaign_batch(
                                session=session,
                                campaign=campaign,
                                user_id=str(campaign.created_by_id),
                            )
                            logger.info(f"Campaign {campaign.id} (tenant: {tenant_name}) batch result: {batch_result}")
                            total_processed.append(str(campaign.id))
                        except Exception as e:
                            logger.exception(f"Error processing campaign {campaign.id}: {e}")
        except Exception as e:
            logger.exception(f"Error checking tenant {tenant_name}: {e}")

    return {
        "tenants_checked": tenants_checked,
        "campaigns_found": total_campaigns_found,
        "campaigns_processed": total_processed,
    }
