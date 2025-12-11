# Campaign Email Sending Architecture

## Overview

The campaign email sending system enables sending marketing emails to campaign recipients with configurable pacing and daily limits. It uses a **background worker** that automatically processes campaigns - no frontend polling required.

## Prerequisites

**IMPORTANT**: Users must have **O365 or Gmail connected** before creating a campaign. The `createCampaign` mutation will return an error if no email provider is linked.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │     │   FastAPI App    │     │ Background      │
│   (React)       │────▶│   (GraphQL)      │     │ Worker          │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                         │
        User calls                                       │ Runs every
        startCampaignSending()                           │ 60 seconds
                                                         │
                        ┌──────────────────┐             │
                        │   PostgreSQL     │◀────────────┘
                        │   Database       │
                        └──────────────────┘
                               │
                        ┌──────┴──────┐
                        ▼             ▼
                   ┌────────┐   ┌──────────┐
                   │ O365   │   │  Gmail   │
                   │ API    │   │  API     │
                   └────────┘   └──────────┘
```

### Components

```
app/workers/
├── __init__.py
├── campaign_worker.py     # Background email processing tasks
└── run_worker.py          # Worker entry point

app/graphql/campaigns/
├── models/
│   └── campaign_send_log_model.py    # Daily send count tracking
├── repositories/
│   └── campaign_send_log_repository.py # Send log data access
├── services/
│   ├── email_provider_service.py      # O365/Gmail abstraction
│   └── campaign_email_sender_service.py # Test email & status
└── strawberry/
    └── campaign_sending_status_response.py # GraphQL types
```

## Frontend Integration Guide

### Step 1: Check Email Provider Status (Optional)

Before showing campaign creation UI, you can check if user has email connected:

```graphql
query {
  o365ConnectionStatus {
    isConnected
    microsoftEmail
  }
  gmailConnectionStatus {
    isConnected
    gmailEmail
  }
}
```

### Step 2: Create Campaign

```graphql
mutation CreateCampaign($input: CampaignInput!) {
  createCampaign(input: $input) {
    id
    name
    status  # Returns "DRAFT"
  }
}
```

**Error if no email provider**:
```json
{
  "errors": [{
    "message": "No email provider connected. Please connect O365 or Gmail before creating a campaign."
  }]
}
```

### Step 3: Send Test Email (Optional)

```graphql
mutation SendTestEmail($campaignId: UUID!, $testEmail: String!) {
  sendTestEmail(campaignId: $campaignId, testEmail: $testEmail) {
    success
    error
  }
}
```

### Step 4: Start Campaign Sending

For **immediate sending**:
```graphql
mutation StartCampaign($campaignId: UUID!) {
  startCampaignSending(campaignId: $campaignId) {
    id
    status  # Returns "SENDING"
  }
}
```

For **scheduled sending**, set `scheduledAt` when creating the campaign and set status to `SCHEDULED`. The backend worker will automatically start sending when the time arrives.

### Step 5: Monitor Progress

Poll this query to show progress (recommended: every 10-30 seconds):

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

### Step 6: Pause/Resume (Optional)

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
   (when scheduled_at time passes - handled by backend worker)
```

### Status Descriptions

| Status | Description | Frontend Action |
|--------|-------------|-----------------|
| `DRAFT` | Campaign created, not started | Show "Start Sending" button |
| `SCHEDULED` | Waiting for scheduled time | Show countdown/scheduled time |
| `SENDING` | Worker is processing emails | Show progress bar, poll status |
| `PAUSED` | User paused the campaign | Show "Resume" button |
| `COMPLETED` | All emails sent | Show completion message |

## Email Status (per recipient)

| Status | Description |
|--------|-------------|
| `PENDING` | Not yet sent |
| `SENT` | Successfully delivered to email provider |
| `FAILED` | Send attempt failed |
| `BOUNCED` | Email bounced (future feature) |

## Running the Worker

The worker runs as a **separate process** from the main FastAPI app:

```bash
# Start the main API server
python start.py

# In another terminal, start the worker
python -m app.workers.run_worker
```

### Production Deployment

Run both processes:
```bash
# API server (handles GraphQL requests)
gunicorn app.api.app:create_app --workers 4

# Campaign worker (processes emails in background)
python -m app.workers.run_worker
```

Or use a process manager like `supervisord`:
```ini
[program:api]
command=python start.py

[program:campaign_worker]
command=python -m app.workers.run_worker
```

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

## Send Pace Configuration

| Pace | Emails/Hour | Batch Size (per minute) |
|------|-------------|------------------------|
| SLOW | 50 | ~1-2 |
| MEDIUM | 200 | ~6-7 |
| FAST | 500 | ~16-17 |

## Daily Limit Enforcement

1. Default limit: **1000 emails/day** per campaign
2. Configurable via `max_emails_per_day` field
3. Tracked in `campaign_send_logs` table
4. Resets at midnight (UTC)

When limit is reached:
- Worker stops processing that campaign for the day
- `canSendMoreToday` returns `false`
- Resumes automatically the next day

## Email Provider Selection

The worker automatically uses the campaign creator's connected email provider:

1. **O365** (preferred if connected)
2. **Gmail** (fallback)

If no provider is connected, campaign creation is blocked.

### Token Refresh

The worker automatically refreshes expired OAuth tokens:
- Checks token expiration before each send (5-minute buffer)
- Refreshes using stored refresh token if expired
- Updates database with new access token
- If refresh fails, marks token as inactive

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No email provider on create | Returns error, blocks creation |
| Token expired | Auto-refresh attempted |
| Token refresh fails | Provider skipped, recipient marked FAILED |
| API rate limit | Retries in next batch |
| Invalid email | Recipient marked FAILED |
| Network error | Logged, retries next cycle |

## File Locations

| File | Purpose |
|------|---------|
| [campaign_worker.py](../app/workers/campaign_worker.py) | Background tasks |
| [run_worker.py](../app/workers/run_worker.py) | Worker entry point |
| [campaign_send_log_model.py](../app/graphql/campaigns/models/campaign_send_log_model.py) | Daily count model |
| [campaigns_service.py](../app/graphql/campaigns/services/campaigns_service.py) | Campaign CRUD with provider check |
| [email_provider_service.py](../app/graphql/campaigns/services/email_provider_service.py) | O365/Gmail abstraction |

## Dependencies

- Microsoft O365 integration (`app/integrations/microsoft_o365/`)
- Gmail integration (`app/integrations/gmail/`)
