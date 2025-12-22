"""GraphQL response type for campaign sending status."""

from uuid import UUID

import strawberry
from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.send_pace import SendPace

from app.graphql.campaigns.services.campaign_email_sender_service import (
    CampaignSendingStatus,
)


@strawberry.type
class CampaignSendingStatusResponse:
    """Response type for campaign sending status."""

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

    @strawberry.field
    def progress_display(self) -> str:
        """Human-readable progress string."""
        return f"{self.sent_count} / {self.total_recipients}"

    @classmethod
    def from_dataclass(
        cls, status: CampaignSendingStatus
    ) -> "CampaignSendingStatusResponse":
        """Create response from service dataclass."""
        return cls(
            campaign_id=status.campaign_id,
            status=status.status,
            total_recipients=status.total_recipients,
            sent_count=status.sent_count,
            pending_count=status.pending_count,
            failed_count=status.failed_count,
            bounced_count=status.bounced_count,
            today_sent_count=status.today_sent_count,
            max_emails_per_day=status.max_emails_per_day,
            remaining_today=status.remaining_today,
            send_pace=status.send_pace,
            emails_per_hour=status.emails_per_hour,
            progress_percentage=status.progress_percentage,
            is_completed=status.is_completed,
            can_send_more_today=status.can_send_more_today,
        )


@strawberry.type
class SendBatchResultResponse:
    """Response type for batch email sending result."""

    emails_sent: int
    emails_failed: int
    emails_remaining: int
    is_completed: bool
    errors: list[str]

    @strawberry.field
    def success(self) -> bool:
        """Whether the batch was successful (at least one email sent)."""
        return self.emails_sent > 0 or self.is_completed


@strawberry.type
class SendTestEmailResponse:
    """Response type for test email sending."""

    success: bool
    error: str | None = None
