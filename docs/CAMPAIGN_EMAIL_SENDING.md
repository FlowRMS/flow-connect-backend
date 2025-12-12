# Campaign Email Sending Architecture

## Overview

The campaign email sending system enables sending marketing emails to campaign recipients with configurable pacing and daily limits. It uses **TaskIQ** with a cron-based scheduler that automatically processes campaigns - no frontend polling required.

## Prerequisites

**IMPORTANT**: Users must have **O365 or Gmail connected** before creating a campaign. The `createCampaign` mutation will return an error if no email provider is linked.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │     │   FastAPI App    │     │ TaskIQ Worker   │
│   (React)       │────▶│   (GraphQL)      │     │ (Separate       │
└─────────────────┘     └──────────────────┘     │  Process)       │
                                                 └────────┬────────┘
        User calls                                        │
        startCampaignSending()                            │ Cron: every
                                                          │ minute
                        ┌──────────────────┐              │
                        │   PostgreSQL     │◀─────────────┘
                        │   (Multi-tenant) │
                        └──────────────────┘
                               │
                        ┌──────┴──────┐
                        ▼             ▼
                   ┌────────┐   ┌──────────┐
                   │ O365   │   │  Gmail   │
                   │ API    │   │  API     │
                   └────────┘   └──────────┘
```

## Worker Components

```
app/workers/
├── __init__.py
├── broker.py                 # TaskIQ broker & scheduler config
├── tasks.py                  # Cron task for campaign processing
├── run_worker.py             # Worker entry point
└── services/
    ├── __init__.py
    └── worker_email_service.py  # Email sending service for workers
```

### Key Files

| File | Purpose |
|------|---------|
| [broker.py](../app/workers/broker.py) | TaskIQ InMemoryBroker + TaskiqScheduler with LabelScheduleSource |
| [tasks.py](../app/workers/tasks.py) | Main `check_and_process_campaigns_task` with cron schedule |
| [run_worker.py](../app/workers/run_worker.py) | Entry point using `run_scheduler_task()` |
| [worker_email_service.py](../app/workers/services/worker_email_service.py) | O365/Gmail sending with token refresh |

## How It Works

### 1. TaskIQ Cron Scheduler

The worker uses TaskIQ's built-in cron scheduling:

```python
# In broker.py
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

broker = RedisStreamBroker(url=redis_url)
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
```

```python
# In tasks.py
CAMPAIGN_PROCESSING_CRON = "* * * * *"  # Every minute

@broker.task(schedule=[{"cron": CAMPAIGN_PROCESSING_CRON}])
async def check_and_process_campaigns_task():
    # Process all tenants and their active campaigns
```

### 2. Multi-Tenant Processing

The worker iterates through all tenant databases:

```python
controller = await get_multitenant_controller(settings)
for tenant_name in controller.ro_engines.keys():
    async with controller.scoped_session(tenant_name) as session:
        # Find campaigns with status SENDING or SCHEDULED
        # Process each campaign
```

### 3. Dependency Injection

Settings are resolved via the DI container:

```python
container = create_container()
async with container.context() as ctx:
    settings = await ctx.resolve(Settings)
    o365_settings = await ctx.resolve(O365Settings)
    gmail_settings = await ctx.resolve(GmailSettings)
```

### 4. Batch Processing

Each run processes a batch of emails based on pace:

```python
PACE_LIMITS = {
    SendPace.SLOW: 50,      # 50 emails/hour
    SendPace.MEDIUM: 75,    # 75 emails/hour
    SendPace.FAST: 100,     # 100 emails/hour
}

# Batch size = emails_per_hour / 30 (roughly 2 minutes worth)
# For MEDIUM: 75 / 30 ≈ 2-3 emails per minute
batch_size = max(1, emails_per_hour // 30)
```

## Running the Worker

The worker runs as a **separate process** from the FastAPI app:

```bash
# Terminal 1: Start the main API server
uv run main.py
# or
python start.py

# Terminal 2: Start the campaign worker
uv run -m app.workers.run_worker
# or
python -m app.workers.run_worker
```

**IMPORTANT**: Running `main.py` does NOT start the worker. You must run the worker separately.

### Production Deployment

Use a process manager or containers:

```bash
# Docker Compose example
services:
  api:
    command: python start.py

  worker:
    command: python -m app.workers.run_worker
```

Or `supervisord`:
```ini
[program:api]
command=python start.py

[program:campaign_worker]
command=python -m app.workers.run_worker
```

## Adjusting the Cron Schedule

The cron schedule is defined in [tasks.py:41](../app/workers/tasks.py#L41):

```python
CAMPAIGN_PROCESSING_CRON = "* * * * *"  # Every minute
```

Common patterns:

| Schedule | Cron Expression |
|----------|-----------------|
| Every minute | `* * * * *` |
| Every 5 minutes | `*/5 * * * *` |
| Every 10 minutes | `*/10 * * * *` |
| Every 30 minutes | `*/30 * * * *` |
| Every hour | `0 * * * *` |

**Note**: If you increase the interval, adjust the batch size calculation accordingly:
```python
# For 5-minute intervals: emails_per_hour // 12 instead of // 30
batch_size = max(1, emails_per_hour // 12)
```

## Send Pace Configuration

| Pace | Emails/Hour | Batch Size (per minute) | Use Case |
|------|-------------|------------------------|----------|
| SLOW | 50 | ~1-2 | Careful sending, new domains |
| MEDIUM | 75 | ~2-3 | Standard campaigns |
| FAST | 100 | ~3-4 | Time-sensitive campaigns |

## Daily Limit Enforcement

1. Default limit: **1000 emails/day** per campaign
2. Configurable via `max_emails_per_day` field
3. Tracked in `campaign_send_logs` table (one record per campaign per day)
4. Resets at midnight UTC

When limit is reached:
- Worker logs "Campaign X reached daily limit of Y"
- Skips that campaign for the day
- `canSendMoreToday` query returns `false`
- Resumes automatically the next day

## Email Provider Selection

The worker uses the campaign creator's connected email provider:

1. **O365** - Tried first if connected
2. **Gmail** - Fallback if O365 not available

### Token Refresh

The `WorkerEmailService` automatically handles OAuth token refresh:

```python
# 5-minute buffer before expiration
TOKEN_REFRESH_BUFFER_SECONDS = 300

async def refresh_o365_token_if_needed(self, session, token):
    now = datetime.now(timezone.utc)
    refresh_threshold = token.expires_at - timedelta(seconds=TOKEN_REFRESH_BUFFER_SECONDS)

    if now < refresh_threshold:
        return token.access_token  # Still valid

    # Refresh the token
    response = await client.post(TOKEN_ENDPOINT, data={...})
    token.access_token = response["access_token"]
    token.expires_at = now + timedelta(seconds=response["expires_in"])
    await session.flush()
```

## GraphQL API

### Start Campaign Sending

```graphql
mutation StartCampaign($campaignId: UUID!) {
  startCampaignSending(campaignId: $campaignId) {
    id
    status  # Returns "SENDING"
  }
}
```

### Monitor Progress

```graphql
query CampaignStatus($campaignId: UUID!) {
  campaignSendingStatus(campaignId: $campaignId) {
    status
    totalRecipients
    sentCount
    pendingCount
    failedCount
    progressPercentage
    progressDisplay      # e.g., "45 / 100"
    isCompleted
    canSendMoreToday
    todaySentCount
    maxEmailsPerDay
    remainingToday
    sendPace
    emailsPerHour
  }
}
```

### Pause/Resume

```graphql
mutation PauseCampaign($id: UUID!) {
  pauseCampaign(id: $id) {
    id
    status  # Returns "PAUSED"
  }
}

mutation ResumeCampaign($id: UUID!) {
  resumeCampaign(id: $id) {
    id
    status  # Returns "SENDING"
  }
}
```

### Send Test Email

```graphql
mutation SendTestEmail($campaignId: UUID!, $testEmail: String!) {
  sendTestEmail(campaignId: $campaignId, testEmail: $testEmail) {
    success
    error
  }
}
```

## Campaign Status Flow

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
DRAFT ──────────▶ SENDING ──────────▶ COMPLETED          │
                    │                                     │
                    ▼                                     │
                 PAUSED ──────────────────────────────────┘
                                    (resume)

SCHEDULED ──────▶ SENDING ──────────▶ COMPLETED
   (when scheduled_at time passes - handled by worker)
```

| Status | Description | Worker Behavior |
|--------|-------------|-----------------|
| `DRAFT` | Not started | Ignored |
| `SCHEDULED` | Waiting for scheduled time | Starts when `scheduled_at <= now` |
| `SENDING` | Actively processing | Processes batch each minute |
| `PAUSED` | User paused | Ignored |
| `COMPLETED` | All emails sent | Ignored |

## Worker Logs

The worker produces detailed logs:

```
============================================================
[2025-12-11 04:44:00 UTC] CAMPAIGN CHECK STARTED
============================================================
[04:44:00] Found 2 tenants to check: ['staging', 'staging2']
[04:44:00] Checking tenant: staging
[04:44:00]   └── Found 1 active campaign(s)
[04:44:00]       └── Processing campaign: 'Welcome Series' (status: SENDING)
[04:44:01]           └── Result: sent=5, failed=0, remaining=45, status=SENDING
[04:44:01] Checking tenant: staging2
[04:44:01]   └── No active campaigns in staging2
------------------------------------------------------------
[2025-12-11 04:44:01 UTC] CAMPAIGN CHECK COMPLETED
  Duration: 0.51s
  Tenants checked: 2
  Campaigns found: 1
  Campaigns processed: 1
============================================================
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No email provider connected | Recipient marked FAILED, logged as warning |
| O365 token expired | Auto-refresh attempted |
| Token refresh fails | Provider skipped, tries Gmail if available |
| API rate limit | Recipient stays PENDING, retried next batch |
| Invalid email address | Recipient marked FAILED |
| Network error | Logged, retried next cycle |

## Database Schema

### campaign_send_logs

Tracks daily email counts per campaign.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| campaign_id | UUID | FK to campaigns |
| send_date | DATE | The date of sending |
| emails_sent | INTEGER | Count sent on this date |
| last_sent_at | TIMESTAMP | Last email sent time |

**Unique constraint**: `(campaign_id, send_date)` - one record per campaign per day

## Known Limitations

1. **No retry queue**: Failed emails are marked FAILED immediately. Consider adding a retry mechanism for transient failures.

2. **No campaign locking**: Currently, users can edit SENDING campaigns. Most CRMs block this - pause first, edit, then resume.

## Future Improvements

- [x] Add Redis broker for multi-instance support
- [ ] Implement retry queue for transient failures
- [ ] Add campaign editing guards (block editing SENDING campaigns)
- [ ] Add bounce tracking via webhooks
- [ ] Add unsubscribe handling
