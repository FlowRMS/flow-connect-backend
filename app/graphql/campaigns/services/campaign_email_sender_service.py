from dataclasses import dataclass
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.campaigns.campaign_model import Campaign
from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.email_status import EmailStatus
from commons.db.v6.crm.campaigns.send_pace import SendPace

from app.errors.common_errors import NotFoundError
from app.graphql.campaigns.repositories.campaign_recipients_repository import (
    CampaignRecipientsRepository,
)
from app.graphql.campaigns.repositories.campaign_send_log_repository import (
    CampaignSendLogRepository,
)
from app.graphql.campaigns.repositories.campaigns_repository import CampaignsRepository
from app.graphql.campaigns.services.email_provider_service import EmailProviderService

# Emails per hour for each pace
PACE_LIMITS: dict[SendPace, int] = {
    SendPace.SLOW: 25,
    SendPace.MEDIUM: 50,
    SendPace.FAST: 100,
}

# Default max emails per day if not specified
DEFAULT_MAX_EMAILS_PER_DAY = 1000


@dataclass
class SendBatchResult:
    """Result of sending a batch of emails."""

    emails_sent: int
    emails_failed: int
    emails_remaining: int
    is_completed: bool
    errors: list[str]


@dataclass
class CampaignSendingStatus:
    """Current sending status of a campaign."""

    campaign_id: UUID
    status: CampaignStatus
    total_recipients: int
    sent_count: int
    pending_count: int
    failed_count: int
    bounced_count: int
    today_sent_count: int
    max_emails_per_day: int
    remaining_today: int
    send_pace: SendPace | None
    emails_per_hour: int
    progress_percentage: float
    is_completed: bool
    can_send_more_today: bool


class CampaignEmailSenderService:
    """
    Service for sending campaign emails with pacing and daily limits.

    Handles:
    - Send pace limits (SLOW: 25/hr, MEDIUM: 50/hr, FAST: 100/hr)
    - Max emails per day limits
    - Status tracking and updates
    - Automatic campaign completion
    """

    def __init__(
        self,
        campaigns_repository: CampaignsRepository,
        recipients_repository: CampaignRecipientsRepository,
        send_log_repository: CampaignSendLogRepository,
        email_provider: EmailProviderService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.campaigns_repository = campaigns_repository
        self.recipients_repository = recipients_repository
        self.send_log_repository = send_log_repository
        self.email_provider = email_provider
        self.auth_info = auth_info

    async def get_sending_status(self, campaign_id: UUID) -> CampaignSendingStatus:
        """Get the current sending status of a campaign."""
        campaign = await self.campaigns_repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        status_counts = await self.recipients_repository.get_status_counts(campaign_id)
        total = sum(status_counts.values())
        sent = status_counts.get(EmailStatus.SENT, 0)
        pending = status_counts.get(EmailStatus.PENDING, 0)
        failed = status_counts.get(EmailStatus.FAILED, 0)
        bounced = status_counts.get(EmailStatus.BOUNCED, 0)

        today_sent = await self.send_log_repository.get_today_sent_count(campaign_id)
        max_per_day = campaign.max_emails_per_day or DEFAULT_MAX_EMAILS_PER_DAY
        remaining_today = max(0, max_per_day - today_sent)

        pace = campaign.send_pace or SendPace.MEDIUM
        emails_per_hour = PACE_LIMITS.get(pace, PACE_LIMITS[SendPace.MEDIUM])

        progress = (sent / total * 100) if total > 0 else 0.0
        is_completed = pending == 0 and total > 0

        return CampaignSendingStatus(
            campaign_id=campaign_id,
            status=campaign.status,
            total_recipients=total,
            sent_count=sent,
            pending_count=pending,
            failed_count=failed,
            bounced_count=bounced,
            today_sent_count=today_sent,
            max_emails_per_day=max_per_day,
            remaining_today=remaining_today,
            send_pace=pace,
            emails_per_hour=emails_per_hour,
            progress_percentage=round(progress, 2),
            is_completed=is_completed,
            can_send_more_today=remaining_today > 0 and pending > 0,
        )

    async def calculate_batch_size(self, campaign: Campaign) -> int:
        """
        Calculate how many emails can be sent in this batch.

        Takes into account:
        - Send pace (emails per hour)
        - Daily limit
        - Remaining recipients
        """
        campaign_id = campaign.id
        pace = campaign.send_pace or SendPace.MEDIUM
        max_per_day = campaign.max_emails_per_day or DEFAULT_MAX_EMAILS_PER_DAY

        # Get today's sent count
        today_sent = await self.send_log_repository.get_today_sent_count(campaign_id)
        remaining_today = max(0, max_per_day - today_sent)

        if remaining_today == 0:
            return 0

        # Get pending count
        pending = await self.recipients_repository.count_by_status(
            campaign_id, EmailStatus.PENDING
        )
        if pending == 0:
            return 0

        # Calculate batch size based on pace
        # For a typical API call interval of ~1 minute, calculate proportional batch
        emails_per_hour = PACE_LIMITS.get(pace, PACE_LIMITS[SendPace.MEDIUM])
        # Send in batches that would take about 1-2 minutes at this pace
        batch_size = max(1, emails_per_hour // 30)  # ~2 minute worth

        # Limit to remaining today and pending
        return min(batch_size, remaining_today, pending)

    async def send_batch(self, campaign_id: UUID) -> SendBatchResult:
        """
        Send a batch of emails for a campaign.

        Respects pace limits and daily limits.
        Returns the result of the batch operation.
        """
        campaign = await self.campaigns_repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        # Check campaign status
        if campaign.status not in (CampaignStatus.SENDING, CampaignStatus.SCHEDULED):
            return SendBatchResult(
                emails_sent=0,
                emails_failed=0,
                emails_remaining=0,
                is_completed=False,
                errors=[
                    f"Campaign is not in SENDING or SCHEDULED status. Current: {campaign.status.name}"
                ],
            )

        # Update to SENDING if scheduled
        if campaign.status == CampaignStatus.SCHEDULED:
            campaign.status = CampaignStatus.SENDING
            await self.campaigns_repository.session.flush()

        # Check if user has email provider connected
        if not await self.email_provider.has_connected_provider():
            return SendBatchResult(
                emails_sent=0,
                emails_failed=0,
                emails_remaining=0,
                is_completed=False,
                errors=["No email provider connected. Please connect O365 or Gmail."],
            )

        # Calculate batch size
        batch_size = await self.calculate_batch_size(campaign)
        if batch_size == 0:
            # Check if daily limit reached or all sent
            pending = await self.recipients_repository.count_by_status(
                campaign_id, EmailStatus.PENDING
            )
            if pending == 0:
                return await self._complete_campaign(campaign)

            return SendBatchResult(
                emails_sent=0,
                emails_failed=0,
                emails_remaining=pending,
                is_completed=False,
                errors=["Daily email limit reached. Try again tomorrow."],
            )

        # Get pending recipients
        recipients = await self.recipients_repository.get_pending_recipients(
            campaign_id, limit=batch_size
        )

        if not recipients:
            return await self._complete_campaign(campaign)

        # Send emails
        sent = 0
        failed = 0
        errors: list[str] = []

        for recipient in recipients:
            result = await self._send_email_to_recipient(campaign, recipient)
            if result.emails_sent > 0:
                sent += 1
            else:
                failed += 1
                if result.errors:
                    errors.append(f"{recipient.contact.email}: {result.errors[0]}")

        # Update send log
        if sent > 0:
            _ = await self.send_log_repository.increment_sent_count(campaign_id, sent)

        # Check if campaign is completed
        remaining = await self.recipients_repository.count_by_status(
            campaign_id, EmailStatus.PENDING
        )

        if remaining == 0:
            return await self._complete_campaign(campaign, sent, failed, errors)

        return SendBatchResult(
            emails_sent=sent,
            emails_failed=failed,
            emails_remaining=remaining,
            is_completed=False,
            errors=errors,
        )

    async def _send_email_to_recipient(
        self,
        campaign: Campaign,
        recipient: CampaignRecipient,
    ) -> "SendBatchResult":
        """Send an email to a single recipient."""
        contact = recipient.contact

        # Check if contact has email
        if not contact.email:
            _ = await self.recipients_repository.mark_as_failed(recipient.id)
            return SendBatchResult(
                emails_sent=0,
                emails_failed=1,
                emails_remaining=0,
                is_completed=False,
                errors=["Contact has no email address"],
            )

        # Prepare email content
        subject = campaign.email_subject or "Campaign Email"
        body = recipient.personalized_content or campaign.email_body or ""

        # Send via provider
        result = await self.email_provider.send_email(
            to=[contact.email],
            subject=subject,
            body=body,
            body_type="HTML",
        )

        # Update recipient status
        if result.success:
            _ = await self.recipients_repository.mark_as_sent(recipient.id)
            return SendBatchResult(
                emails_sent=1,
                emails_failed=0,
                emails_remaining=0,
                is_completed=False,
                errors=[],
            )

        _ = await self.recipients_repository.mark_as_failed(recipient.id)
        return SendBatchResult(
            emails_sent=0,
            emails_failed=1,
            emails_remaining=0,
            is_completed=False,
            errors=[result.error or "Unknown error"],
        )

    async def _complete_campaign(
        self,
        campaign: Campaign,
        sent: int = 0,
        failed: int = 0,
        errors: list[str] | None = None,
    ) -> SendBatchResult:
        """Mark a campaign as completed."""
        campaign.status = CampaignStatus.COMPLETED
        await self.campaigns_repository.session.flush()

        return SendBatchResult(
            emails_sent=sent,
            emails_failed=failed,
            emails_remaining=0,
            is_completed=True,
            errors=errors or [],
        )

    async def send_test_email(
        self,
        campaign_id: UUID,
        test_email: str,
    ) -> SendBatchResult:
        """Send a test email for a campaign to a specific email address."""
        campaign = await self.campaigns_repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        # Check if user has email provider connected
        if not await self.email_provider.has_connected_provider():
            return SendBatchResult(
                emails_sent=0,
                emails_failed=1,
                emails_remaining=0,
                is_completed=False,
                errors=["No email provider connected. Please connect O365 or Gmail."],
            )

        # Prepare email content
        subject = f"[TEST] {campaign.email_subject or 'Campaign Email'}"
        body = campaign.email_body or ""

        # Send via provider
        result = await self.email_provider.send_email(
            to=[test_email],
            subject=subject,
            body=body,
            body_type="HTML",
        )

        if result.success:
            return SendBatchResult(
                emails_sent=1,
                emails_failed=0,
                emails_remaining=0,
                is_completed=False,
                errors=[],
            )

        return SendBatchResult(
            emails_sent=0,
            emails_failed=1,
            emails_remaining=0,
            is_completed=False,
            errors=[result.error or "Failed to send test email"],
        )

    async def start_campaign(self, campaign_id: UUID) -> Campaign:
        """Start sending a campaign by setting its status to SENDING."""
        campaign = await self.campaigns_repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        if campaign.status not in (CampaignStatus.DRAFT, CampaignStatus.PAUSED):
            raise ValueError(f"Cannot start campaign in {campaign.status.name} status")

        campaign.status = CampaignStatus.SENDING
        await self.campaigns_repository.session.flush()
        return await self.campaigns_repository.get_with_relations(campaign_id)  # type: ignore[return-value]
