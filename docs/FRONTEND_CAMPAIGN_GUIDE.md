# Frontend Campaign Sending Guide

This document explains how to integrate campaign email sending features in the frontend.

## Prerequisites

**Users MUST have O365 or Gmail connected before creating a campaign.**

If no email provider is connected, the `createCampaign` mutation will fail with:
```json
{
  "errors": [{
    "message": "No email provider connected. Please connect O365 or Gmail before creating a campaign."
  }]
}
```

### Check Email Provider Status

Before showing the campaign creation UI, check if the user has an email provider:

```graphql
query CheckEmailProviders {
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

**Frontend Logic:**
```typescript
const hasEmailProvider = data.o365ConnectionStatus.isConnected || data.gmailConnectionStatus.isConnected;

if (!hasEmailProvider) {
  // Show message: "Please connect O365 or Gmail to create campaigns"
  // Redirect to integrations settings
}
```

---

## Campaign Lifecycle

```
┌─────────┐     ┌─────────┐     ┌───────────┐     ┌───────────┐
│  DRAFT  │────▶│ SENDING │────▶│ COMPLETED │     │  PAUSED   │
└─────────┘     └────┬────┘     └───────────┘     └─────┬─────┘
                     │                                   │
                     └───────────▶ PAUSED ◀──────────────┘
                                     │
                                     └──────▶ SENDING (resume)

┌───────────┐     ┌─────────┐     ┌───────────┐
│ SCHEDULED │────▶│ SENDING │────▶│ COMPLETED │
└───────────┘     └─────────┘     └───────────┘
   (auto at scheduled_at time - backend handles this)
```

---

## Step-by-Step Integration

### 1. Create Campaign

```graphql
mutation CreateCampaign($input: CampaignInput!) {
  createCampaign(input: $input) {
    id
    name
    status
    recipientsCount
    sendPace
    maxEmailsPerDay
    scheduledAt
  }
}
```

**Variables Example (Immediate Send):**
```json
{
  "input": {
    "name": "Summer Sale Campaign",
    "emailSubject": "Don't miss our summer sale!",
    "emailBody": "<h1>Summer Sale</h1><p>50% off everything!</p>",
    "recipientListType": "STATIC",
    "staticContactIds": ["uuid1", "uuid2", "uuid3"],
    "sendPace": "MEDIUM",
    "maxEmailsPerDay": 500,
    "sendImmediately": true
  }
}
```

**Variables Example (Scheduled Send):**
```json
{
  "input": {
    "name": "New Year Campaign",
    "emailSubject": "Happy New Year!",
    "emailBody": "<h1>Happy 2025!</h1>",
    "recipientListType": "CRITERIA_BASED",
    "criteria": {
      "groups": [...],
      "groupOperator": "AND"
    },
    "sendPace": "SLOW",
    "maxEmailsPerDay": 100,
    "sendImmediately": false,
    "scheduledAt": "2025-01-01T00:00:00Z"
  }
}
```

---

### 2. Send Test Email (Optional but Recommended)

Before starting the campaign, let users send a test email:

```graphql
mutation SendTestEmail($campaignId: UUID!, $testEmail: String!) {
  sendTestEmail(campaignId: $campaignId, testEmail: $testEmail) {
    success
    error
  }
}
```

**Frontend UI:**
- Show input field for test email address
- Show "Send Test" button
- Display success/error message

```typescript
if (data.sendTestEmail.success) {
  showToast("Test email sent! Check your inbox.");
} else {
  showToast(`Failed: ${data.sendTestEmail.error}`, "error");
}
```

---

### 3. Start Campaign Sending

#### For Immediate Sending:

```graphql
mutation StartCampaignSending($campaignId: UUID!) {
  startCampaignSending(campaignId: $campaignId) {
    id
    status
    recipientsCount
    sentCount
  }
}
```

After this mutation:
- Status changes to `SENDING`
- Backend worker automatically picks it up within 60 seconds
- Emails start sending at the configured pace

#### For Scheduled Sending:

No additional mutation needed. When creating the campaign:
1. Set `sendImmediately: false`
2. Set `scheduledAt` to the desired datetime
3. Set status to `SCHEDULED` (or backend sets it automatically)

The backend worker will:
- Check every 60 seconds for scheduled campaigns
- When `scheduled_at` time passes, automatically change status to `SENDING`
- Start processing emails

---

### 4. Monitor Campaign Progress

Poll this query while campaign is `SENDING`:

```graphql
query CampaignSendingStatus($campaignId: UUID!) {
  campaignSendingStatus(campaignId: $campaignId) {
    campaignId
    status
    totalRecipients
    sentCount
    pendingCount
    failedCount
    bouncedCount
    todaySentCount
    maxEmailsPerDay
    remainingToday
    sendPace
    emailsPerHour
    progressPercentage
    progressDisplay
    isCompleted
    canSendMoreToday
  }
}
```

**Response Example:**
```json
{
  "data": {
    "campaignSendingStatus": {
      "campaignId": "abc-123",
      "status": "SENDING",
      "totalRecipients": 1000,
      "sentCount": 450,
      "pendingCount": 550,
      "failedCount": 0,
      "bouncedCount": 0,
      "todaySentCount": 450,
      "maxEmailsPerDay": 500,
      "remainingToday": 50,
      "sendPace": "MEDIUM",
      "emailsPerHour": 200,
      "progressPercentage": 45.0,
      "progressDisplay": "450 / 1000",
      "isCompleted": false,
      "canSendMoreToday": true
    }
  }
}
```

**Frontend Implementation:**

```typescript
// Poll every 10-30 seconds while status is SENDING
useEffect(() => {
  if (campaign.status !== 'SENDING') return;

  const interval = setInterval(() => {
    refetchCampaignStatus();
  }, 15000); // 15 seconds

  return () => clearInterval(interval);
}, [campaign.status]);
```

**Progress Bar UI:**
```typescript
<ProgressBar
  value={data.progressPercentage}
  label={data.progressDisplay}  // "450 / 1000"
/>

{!data.canSendMoreToday && (
  <Alert>Daily limit reached. Sending will resume tomorrow.</Alert>
)}

{data.isCompleted && (
  <Alert type="success">Campaign completed!</Alert>
)}
```

---

### 5. Pause Campaign

```graphql
mutation PauseCampaign($id: UUID!) {
  pauseCampaign(id: $id) {
    id
    status
    sentCount
    recipientsCount
  }
}
```

- Status changes to `PAUSED`
- Worker stops processing this campaign
- Already-sent emails are not affected

**Show Pause button when:** `status === 'SENDING'`

---

### 6. Resume Campaign

```graphql
mutation ResumeCampaign($id: UUID!) {
  resumeCampaign(id: $id) {
    id
    status
    sentCount
    recipientsCount
  }
}
```

- Status changes back to `SENDING`
- Worker picks it up in the next cycle (within 60 seconds)
- Continues from where it left off

**Show Resume button when:** `status === 'PAUSED'`

---

## Campaign List (Landing Page)

The `findLandingPage` query for campaigns automatically includes:
- `recipientsCount` - Total recipients
- `sentCount` - Emails already sent
- `status` - Current campaign status
- `progress` - Computed field showing "sent / total"

```graphql
query CampaignsList($page: PageInput!) {
  findLandingPage(page: $page) {
    data {
      ... on CampaignLandingPage {
        id
        name
        status
        recipientsCount
        sentCount
        progress        # "450 / 1000"
        scheduledAt
      }
    }
    totalCount
  }
}
```

**These values update automatically** as the worker sends emails. No additional polling needed for list views - just refetch when user navigates back to the list.

---

## Status Reference

### Campaign Status

| Status | Description | UI Actions |
|--------|-------------|------------|
| `DRAFT` | Campaign created, not started | Show "Start Sending" or "Schedule" button |
| `SCHEDULED` | Waiting for scheduled time | Show scheduled datetime, "Cancel Schedule" option |
| `SENDING` | Actively sending emails | Show progress bar, "Pause" button |
| `PAUSED` | User paused the campaign | Show "Resume" button, current progress |
| `COMPLETED` | All emails sent | Show final stats, completion message |

### Email Status (per recipient)

| Status | Description |
|--------|-------------|
| `PENDING` | Email not yet sent |
| `SENT` | Email successfully sent to provider |
| `FAILED` | Email send failed |
| `BOUNCED` | Email bounced (future feature) |

---

## Send Pace Reference

| Pace | Emails/Hour | Use Case |
|------|-------------|----------|
| `SLOW` | 50 | Small lists, careful sending |
| `MEDIUM` | 200 | Default, balanced approach |
| `FAST` | 500 | Large lists, time-sensitive |

---

## Error Handling

### Common Errors

| Error | Cause | Frontend Action |
|-------|-------|-----------------|
| "No email provider connected" | User hasn't connected O365/Gmail | Redirect to integrations |
| "Campaign not found" | Invalid campaign ID | Show error, redirect to list |
| "Cannot start campaign in X status" | Campaign not in DRAFT/PAUSED | Refresh campaign data |
| "Daily limit reached" | `maxEmailsPerDay` hit | Show message, will resume tomorrow |

### Example Error Handling

```typescript
try {
  await startCampaignSending({ variables: { campaignId } });
} catch (error) {
  if (error.message.includes("No email provider")) {
    router.push("/settings/integrations");
  } else if (error.message.includes("Cannot start")) {
    refetchCampaign(); // Status may have changed
  } else {
    showToast(error.message, "error");
  }
}
```

---

## Complete Flow Example

```typescript
// 1. Check email provider on page load
const { data: providers } = useQuery(CHECK_EMAIL_PROVIDERS);
const hasProvider = providers?.o365ConnectionStatus.isConnected ||
                    providers?.gmailConnectionStatus.isConnected;

// 2. Create campaign
const [createCampaign] = useMutation(CREATE_CAMPAIGN);
const campaign = await createCampaign({ variables: { input: formData } });

// 3. Optional: Send test email
const [sendTest] = useMutation(SEND_TEST_EMAIL);
await sendTest({
  variables: {
    campaignId: campaign.id,
    testEmail: "test@example.com"
  }
});

// 4. Start sending
const [startSending] = useMutation(START_CAMPAIGN_SENDING);
await startSending({ variables: { campaignId: campaign.id } });

// 5. Poll for progress
const { data: status } = useQuery(CAMPAIGN_SENDING_STATUS, {
  variables: { campaignId: campaign.id },
  pollInterval: campaign.status === 'SENDING' ? 15000 : 0,
});

// 6. Display progress
<CampaignProgress
  sent={status.sentCount}
  total={status.totalRecipients}
  percentage={status.progressPercentage}
  isCompleted={status.isCompleted}
/>

// 7. Pause/Resume controls
{status.status === 'SENDING' && (
  <Button onClick={() => pauseCampaign({ variables: { id: campaign.id } })}>
    Pause
  </Button>
)}
{status.status === 'PAUSED' && (
  <Button onClick={() => resumeCampaign({ variables: { id: campaign.id } })}>
    Resume
  </Button>
)}
```

---

## GraphQL Schema Quick Reference

### Mutations

```graphql
# Create campaign (fails if no email provider)
createCampaign(input: CampaignInput!): CampaignResponse!

# Send test email
sendTestEmail(campaignId: UUID!, testEmail: String!): SendTestEmailResponse!

# Start sending (DRAFT → SENDING)
startCampaignSending(campaignId: UUID!): CampaignResponse!

# Pause (SENDING → PAUSED)
pauseCampaign(id: UUID!): CampaignResponse!

# Resume (PAUSED → SENDING)
resumeCampaign(id: UUID!): CampaignResponse!
```

### Queries

```graphql
# Get campaign details
campaign(id: UUID!): CampaignResponse!

# Get sending status (use for progress monitoring)
campaignSendingStatus(campaignId: UUID!): CampaignSendingStatusResponse!

# Get recipients list
campaignRecipients(campaignId: UUID!, limit: Int, offset: Int): [CampaignRecipientResponse!]!
```

### Types

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
  progressDisplay: String!    # "450 / 1000"
  isCompleted: Boolean!
  canSendMoreToday: Boolean!
}

type SendTestEmailResponse {
  success: Boolean!
  error: String
}

enum CampaignStatus {
  DRAFT
  SCHEDULED
  SENDING
  PAUSED
  COMPLETED
}

enum SendPace {
  SLOW      # 50/hour
  MEDIUM    # 200/hour
  FAST      # 500/hour
}
```
