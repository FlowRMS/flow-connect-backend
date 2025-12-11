# Campaigns Module Architecture

## Overview

The Campaigns module enables email marketing campaigns with three recipient list types:
- **Static List**: Manually selected contacts
- **Criteria-Based**: Filter contacts by conditions (generated once at creation)
- **Dynamic Rules**: Auto-updating list that evaluates criteria daily

## Directory Structure

```
app/graphql/campaigns/
├── __init__.py
├── models/
│   ├── campaign_model.py          # Campaign entity
│   ├── campaign_recipient_model.py # Links campaigns to contacts
│   ├── campaign_criteria_model.py  # Stores filter rules as JSON
│   ├── campaign_send_log_model.py  # Daily email count tracking
│   ├── campaign_status.py          # DRAFT, SCHEDULED, SENDING, COMPLETED, PAUSED
│   ├── recipient_list_type.py      # STATIC, CRITERIA_BASED, DYNAMIC
│   ├── email_status.py             # PENDING, SENT, FAILED, BOUNCED
│   └── send_pace.py                # SLOW(50/hr), MEDIUM(200/hr), FAST(500/hr)
├── repositories/
│   ├── campaigns_repository.py     # Campaign CRUD + landing page query
│   ├── campaign_recipients_repository.py # Recipient operations
│   └── campaign_send_log_repository.py   # Daily send log operations
├── services/
│   ├── campaigns_service.py        # Business logic for campaigns
│   ├── criteria_evaluator_service.py # Dynamic SQL query builder
│   ├── email_provider_service.py   # O365/Gmail abstraction layer
│   └── campaign_email_sender_service.py # Email sending with pacing
├── queries/
│   └── campaigns_queries.py        # GraphQL queries
├── mutations/
│   └── campaigns_mutations.py      # GraphQL mutations
└── strawberry/
    ├── campaign_input.py           # Input for create/update
    ├── campaign_response.py        # Full campaign response
    ├── campaign_landing_page_response.py # List view response
    ├── campaign_recipient_response.py    # Recipient with contact
    ├── campaign_sending_status_response.py # Sending status response
    ├── criteria_input.py           # Criteria condition/group inputs
    └── estimate_recipients_response.py   # Preview count response
```

## Database Schema

### campaigns
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Campaign name |
| status | INTEGER | CampaignStatus enum |
| recipient_list_type | INTEGER | RecipientListType enum |
| description | TEXT | Optional description |
| email_subject | VARCHAR(500) | Email subject line |
| email_body | TEXT | Email content |
| ai_personalization_enabled | BOOLEAN | Enable AI personalization |
| send_pace | INTEGER | SendPace enum |
| max_emails_per_day | INTEGER | Daily limit |
| scheduled_at | TIMESTAMP | For scheduled sends |
| send_immediately | BOOLEAN | Send now flag |
| created_at | TIMESTAMP | Creation timestamp |
| created_by_id | UUID | Creator user ID |

### campaign_recipients
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| campaign_id | UUID | FK to campaigns |
| contact_id | UUID | FK to contacts |
| email_status | INTEGER | EmailStatus enum |
| sent_at | TIMESTAMP | When email was sent |
| personalized_content | TEXT | AI-personalized content |

### campaign_criteria
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| campaign_id | UUID | FK to campaigns (unique) |
| criteria_json | JSONB | Filter rules |
| is_dynamic | BOOLEAN | True for auto-updating |

### campaign_send_logs
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| campaign_id | UUID | FK to campaigns |
| send_date | DATE | The date of sending |
| emails_sent | INTEGER | Count sent on this date |
| last_sent_at | TIMESTAMP | Last email sent time |

**Unique constraint**: `(campaign_id, send_date)` - one record per campaign per day

## GraphQL API

### Queries

```graphql
# Get single campaign with all details
campaign(id: UUID!): CampaignResponse

# Get paginated recipients for a campaign
campaignRecipients(
  campaignId: UUID!
  limit: Int = 100
  offset: Int = 0
): [CampaignRecipientResponse!]!

# Preview recipient count and sample contacts before saving
# Returns full contact info for display in UI
estimateRecipients(
  criteria: CampaignCriteriaInput!
  sampleLimit: Int = 10
): EstimateRecipientsResponse

# Get campaigns list via landing page system
findLandingPages(sourceType: CAMPAIGNS): GenericLandingPage

# Get real-time sending status of a campaign
campaignSendingStatus(campaignId: UUID!): CampaignSendingStatusResponse
```

### EstimateRecipientsResponse

```graphql
type EstimateRecipientsResponse {
  count: Int!                        # Total matching contacts
  sampleContacts: [ContactResponse!]! # Sample contacts with full info
}

type ContactResponse {
  id: UUID!
  createdAt: DateTime!
  firstName: String!
  lastName: String!
  email: String
  phone: String
  role: String
  territory: String
  tags: [String!]
  notes: String
}
```

### Mutations

```graphql
# Create campaign with static IDs or criteria
createCampaign(input: CampaignInput!): CampaignResponse

# Update existing campaign
updateCampaign(id: UUID!, input: CampaignInput!): CampaignResponse

# Delete campaign and recipients
deleteCampaign(id: UUID!): Boolean

# Pause/resume sending
pauseCampaign(id: UUID!): CampaignResponse
resumeCampaign(id: UUID!): CampaignResponse

# Re-evaluate dynamic criteria and add new matches
refreshDynamicRecipients(campaignId: UUID!): CampaignResponse

# Send test email to verify campaign content
sendTestEmail(campaignId: UUID!, testEmail: String!): SendTestEmailResponse

# Start campaign sending - background worker handles the rest
startCampaignSending(campaignId: UUID!): CampaignResponse
```

### CampaignSendingStatusResponse

```graphql
type CampaignSendingStatusResponse {
  campaignId: UUID!
  status: CampaignStatus!
  totalRecipients: Int!
  sentCount: Int!
  pendingCount: Int!
  failedCount: Int!
  bouncedCount: Int!
  todaySentCount: Int!
  maxEmailsPerDay: Int!
  remainingToday: Int!
  sendPace: SendPace
  emailsPerHour: Int!
  progressPercentage: Float!
  isCompleted: Boolean!
  canSendMoreToday: Boolean!
  progressDisplay: String!  # "sent_count / total_recipients"
}
```

## Criteria System

### Input Types

```graphql
input CriteriaConditionInput {
  entityType: CRMEntityType!  # CONTACT, JOB, COMPANY, TASK
  field: String!              # Field name on entity
  operator: CriteriaOperator! # EQUALS, CONTAINS, etc.
  value: JSON                 # Comparison value
}

input CriteriaGroupInput {
  logicalOperator: LogicalOperator!  # AND, OR
  conditions: [CriteriaConditionInput!]!
}

input CampaignCriteriaInput {
  groups: [CriteriaGroupInput!]!
  groupOperator: LogicalOperator!  # Combine groups
}
```

### Operators

- `EQUALS`, `NOT_EQUALS`
- `CONTAINS`, `NOT_CONTAINS` (case-insensitive)
- `GREATER_THAN`, `LESS_THAN`
- `GREATER_THAN_OR_EQUALS`, `LESS_THAN_OR_EQUALS`
- `IS_NULL`, `IS_NOT_NULL`
- `IN`, `NOT_IN`

### How Criteria Evaluation Works

1. **Direct Contact Fields**: When `entityType: CONTACT`, queries the Contact table directly
2. **Linked Entities**: For JOB, COMPANY, TASK, joins through LinkRelation to find contacts linked to matching entities

Example: Find contacts linked to jobs with status "BID":
```json
{
  "groups": [{
    "logicalOperator": "AND",
    "conditions": [{
      "entityType": "JOB",
      "field": "status_id",
      "operator": "EQUALS",
      "value": "job-status-uuid"
    }]
  }],
  "groupOperator": "AND"
}
```

## Recipient List Types

### Static List
- Frontend uses `contactSearch` query to find contacts
- Passes `static_contact_ids: [UUID]` to `createCampaign`
- Recipients are fixed at creation

### Criteria-Based
- Frontend builds criteria with conditions and groups
- Uses `estimateRecipients` to preview count
- Passes `criteria: CampaignCriteriaInput` to `createCampaign`
- Recipients generated once at creation

### Dynamic Rules
- Same as criteria-based, but sets `recipient_list_type: DYNAMIC`
- Criteria stored with `is_dynamic: true`
- Use `refreshDynamicRecipients` to add new matching contacts
- Existing recipients preserved, only new matches added

## Status Derivation

Campaign status is **automatically derived** from input fields - DO NOT send `status` in the mutation input:

| Condition | Derived Status |
|-----------|----------------|
| `sendImmediately: true` | `SENDING` |
| `scheduledAt` is set | `SCHEDULED` |
| Neither | `DRAFT` |

This logic is in [campaign_input.py](../app/graphql/campaigns/strawberry/campaign_input.py) `_derive_status()` method.

## Integration Points

### Landing Page System
- Added `CAMPAIGNS` to `LandingSourceType` enum
- Added `CampaignLandingPageResponse` to `LandingRecord` union
- Added `campaigns_repository` to `LandingPageService`
- Query: `findLandingPages(sourceType: CAMPAIGNS)`

### Response Fields
- `recipients_count`: Total recipients
- `sent_count`: Recipients with SENT status
- `progress`: Computed as "sent_count / recipients_count"

## File Dependencies

### Modified Existing Files
1. `app/graphql/common/landing_source_type.py` - Added CAMPAIGNS enum
2. `app/graphql/common/paginated_landing_page.py` - Added to union
3. `app/graphql/common/services/landing_page_service.py` - Added repository

### New Files Created
- All files under `app/graphql/campaigns/`
- `alembic/versions/20251210_add_campaigns.py` - Database migration
- `alembic/versions/20251211_add_campaign_send_logs.py` - Send logs migration
- `tests/campaigns/test_campaigns.py` - Unit tests

## Email Sending

For detailed documentation on email sending functionality, see [CAMPAIGN_EMAIL_SENDING.md](./CAMPAIGN_EMAIL_SENDING.md).

### Quick Overview

Email sending is handled by a **background worker** - no frontend polling required:

1. **Start Campaign**: Call `startCampaignSending` to set status to SENDING
2. **Background Worker**: Automatically processes campaigns every 60 seconds
3. **Monitor Progress**: Use `campaignSendingStatus` query
4. **Control**: Use `pauseCampaign` / `resumeCampaign` as needed

### Running the Worker

```bash
# API server
python start.py

# Worker (separate process)
python -m app.workers.run_worker
```

### Send Pace

| Pace | Emails/Hour |
|------|-------------|
| SLOW | 50 |
| MEDIUM | 200 |
| FAST | 500 |

### Daily Limits

- Default: 1000 emails/day per campaign
- Configurable via `max_emails_per_day` field
- Enforced via `campaign_send_logs` table
- Resets automatically each day
