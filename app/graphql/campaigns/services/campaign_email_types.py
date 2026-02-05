from dataclasses import dataclass
from uuid import UUID

from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.send_pace import SendPace

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
    emails_sent: int
    emails_failed: int
    emails_remaining: int
    is_completed: bool
    errors: list[str]


@dataclass
class CampaignSendingStatus:
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
