# Campaigns Frontend Integration Guide

## Overview

This document describes how to integrate the Campaigns backend API with the frontend.

## GraphQL Endpoints

### 1. Campaign List (Landing Page)

**Query:**
```graphql
query GetCampaigns($limit: Int, $offset: Int) {
  findLandingPages(
    sourceType: CAMPAIGNS
    limit: $limit
    offset: $offset
  ) {
    records {
      ... on CampaignLandingPage {
        id
        createdAt
        createdBy
        name
        status
        recipientListType
        recipientsCount
        sentCount
        progress
      }
    }
    total
  }
}
```

**Response Fields:**
- `name`: Campaign name
- `status`: DRAFT, SCHEDULED, SENDING, COMPLETED, PAUSED
- `recipientListType`: STATIC, CRITERIA_BASED, DYNAMIC
- `recipientsCount`: Total number of recipients
- `sentCount`: Number of emails sent
- `progress`: String like "45 / 100"

---

### 2. Get Single Campaign

**Query:**
```graphql
query GetCampaign($id: UUID!) {
  campaign(id: $id) {
    id
    createdAt
    name
    status
    recipientListType
    description
    emailSubject
    emailBody
    aiPersonalizationEnabled
    sendPace
    maxEmailsPerDay
    scheduledAt
    sendImmediately
    recipientsCount
    sentCount
    criteriaJson
  }
}
```

**Response Fields:**
- `criteriaJson`: The stored criteria (for editing criteria-based/dynamic campaigns)
- All other campaign fields

---

### 3. Get Campaign Recipients

**Query:**
```graphql
query GetCampaignRecipients($campaignId: UUID!, $limit: Int, $offset: Int) {
  campaignRecipients(campaignId: $campaignId, limit: $limit, offset: $offset) {
    id
    campaignId
    contactId
    emailStatus
    sentAt
    personalizedContent
    contact {
      id
      firstName
      lastName
      email
      phone
      role
    }
  }
}
```

Use this to show the list of recipients when editing a campaign.

---

### 4. Estimate Recipients (Before Creating)

**Query:**
```graphql
query EstimateRecipients($criteria: CampaignCriteriaInput!, $sampleLimit: Int) {
  estimateRecipients(criteria: $criteria, sampleLimit: $sampleLimit) {
    count
    sampleContacts {
      id
      firstName
      lastName
      email
      phone
      role
      territory
      tags
    }
  }
}
```

**Response Fields:**
- `count`: Total number of contacts matching the criteria
- `sampleContacts`: List of actual Contact objects (up to `sampleLimit`, default 10)

**Use Case:** Call this when user builds criteria to:
1. Show "45 recipients match your criteria"
2. Display a preview list of the matching contacts with their names and emails

---

### 5. Contact Search (For Static List)

**Query:**
```graphql
query SearchContacts($searchTerm: String!, $limit: Int) {
  contactSearch(searchTerm: $searchTerm, limit: $limit) {
    id
    firstName
    lastName
    email
    phone
    role
  }
}
```

Use this existing query for the Static List type to search and select contacts.

---

### 6. Create Campaign

**Mutation:**
```graphql
mutation CreateCampaign($input: CampaignInput!) {
  createCampaign(input: $input) {
    id
    name
    status
    recipientsCount
  }
}
```

**Input Types:**

For **Static List**:
```javascript
{
  name: "Q1 Product Launch",
  recipientListType: "STATIC",
  description: "Launch campaign for Q1",
  emailSubject: "Introducing Our New Product",
  emailBody: "Hello {{first_name}}, ...",
  aiPersonalizationEnabled: true,
  sendPace: "MEDIUM",
  maxEmailsPerDay: 50,
  scheduledAt: null,
  sendImmediately: true,
  staticContactIds: ["uuid1", "uuid2", "uuid3"]
}
```

For **Criteria-Based**:
```javascript
{
  name: "Healthcare Sector Campaign",
  recipientListType: "CRITERIA_BASED",
  description: "Target healthcare contacts",
  emailSubject: "Healthcare Solutions",
  emailBody: "Dear {{first_name}}, ...",
  aiPersonalizationEnabled: true,
  sendPace: "SLOW",
  maxEmailsPerDay: 50,
  scheduledAt: "2024-11-25T09:00:00Z",
  sendImmediately: false,
  criteria: {
    groups: [{
      logicalOperator: "AND",
      conditions: [{
        entityType: "CONTACT",
        field: "role",
        operator: "CONTAINS",
        value: "Manager"
      }]
    }],
    groupOperator: "AND"
  }
}
```

For **Dynamic Rules**:
```javascript
{
  name: "Active Projects Follow-up",
  recipientListType: "DYNAMIC",
  // ... same as criteria-based
  criteria: {
    groups: [{
      logicalOperator: "AND",
      conditions: [{
        entityType: "JOB",
        field: "job_name",
        operator: "CONTAINS",
        value: "Active"
      }]
    }],
    groupOperator: "AND"
  }
}
```

---

### 7. Update Campaign

**Mutation:**
```graphql
mutation UpdateCampaign($id: UUID!, $input: CampaignInput!) {
  updateCampaign(id: $id, input: $input) {
    id
    name
    status
  }
}
```

---

### 8. Delete Campaign

**Mutation:**
```graphql
mutation DeleteCampaign($id: UUID!) {
  deleteCampaign(id: $id)
}
```

---

### 9. Pause/Resume Campaign

**Mutations:**
```graphql
mutation PauseCampaign($id: UUID!) {
  pauseCampaign(id: $id) {
    id
    status
  }
}

mutation ResumeCampaign($id: UUID!) {
  resumeCampaign(id: $id) {
    id
    status
  }
}
```

---

### 10. Refresh Dynamic Recipients

**Mutation:**
```graphql
mutation RefreshDynamicRecipients($campaignId: UUID!) {
  refreshDynamicRecipients(campaignId: $campaignId) {
    id
    recipientsCount
  }
}
```

Use this to add new contacts that now match the criteria.

---

### 11. Send Test Email

**Mutation:**
```graphql
mutation SendTestEmail($campaignId: UUID!, $testEmail: String!) {
  sendTestEmail(campaignId: $campaignId, testEmail: $testEmail)
}
```

---

## Criteria Building

### Entity Types
- `CONTACT` - Query contact fields directly
- `JOB` - Find contacts linked to matching jobs
- `COMPANY` - Find contacts linked to matching companies
- `TASK` - Find contacts linked to matching tasks

### Available Fields by Entity

**Contact:**
- `first_name`, `last_name`, `email`, `phone`, `role`, `territory`, `tags`

**Job:**
- `job_name`, `status_id`, `job_type`, `start_date`, `end_date`, `tags`

**Company:**
- `name`, `company_source_type`, `website`, `phone`, `tags`

**Task:**
- `title`, `status`, `priority`, `due_date`, `tags`

### Operators
```javascript
const operators = [
  { value: "EQUALS", label: "Equals" },
  { value: "NOT_EQUALS", label: "Not Equals" },
  { value: "CONTAINS", label: "Contains" },
  { value: "NOT_CONTAINS", label: "Does Not Contain" },
  { value: "GREATER_THAN", label: "Greater Than" },
  { value: "LESS_THAN", label: "Less Than" },
  { value: "IS_NULL", label: "Is Empty" },
  { value: "IS_NOT_NULL", label: "Is Not Empty" },
  { value: "IN", label: "Is One Of" },
  { value: "NOT_IN", label: "Is Not One Of" }
];
```

---

## UI Mapping

### Campaign List Page
- Query: `findLandingPages(sourceType: CAMPAIGNS)`
- Display columns: Name, Status, Recipients, Date, Progress, Actions

### New Campaign Page

**Recipient List Type Selection:**
1. **Static List**: Show contact search + selection
2. **Criteria-Based**: Show criteria builder + estimate count
3. **Dynamic Rules**: Same as criteria-based (with info about auto-updates)

**Form Fields:**
- Campaign Name
- Recipient List Type (toggle)
- Email Subject
- Email Body
- AI Personalization checkbox
- Send Pace dropdown
- Max Emails Per Day
- When to Send (Immediately / Schedule)
- Date/Time picker (if scheduled)

**Actions:**
- Preview Email
- Send Test Email
- Create Campaign
- Save as Draft

### Edit Campaign Page
- Query: `campaign(id)` to load details
- Query: `campaignRecipients(campaignId)` to show recipients
- Use same form as create, populate from response
- `criteriaJson` contains the stored criteria for criteria-based/dynamic

---

## Status Badges

```javascript
const statusColors = {
  DRAFT: "gray",
  SCHEDULED: "yellow",
  SENDING: "blue",
  COMPLETED: "green",
  PAUSED: "orange"
};
```

---

## IMPORTANT: Status is Derived Automatically

**DO NOT send `status` in the mutation input.** The backend automatically derives the status:

| Your Input | Resulting Status |
|------------|------------------|
| `sendImmediately: true` | `SENDING` |
| `scheduledAt` is set | `SCHEDULED` |
| Neither | `DRAFT` |

**Example: Save as Draft**
```javascript
{
  name: "My Campaign",
  recipientListType: "STATIC",
  sendImmediately: false,
  // scheduledAt: null (not set)
  // Result: status will be DRAFT
}
```

**Example: Schedule for Later**
```javascript
{
  name: "My Campaign",
  recipientListType: "STATIC",
  sendImmediately: false,
  scheduledAt: "2024-12-25T09:00:00Z"
  // Result: status will be SCHEDULED
}
```

**Example: Send Now**
```javascript
{
  name: "My Campaign",
  recipientListType: "STATIC",
  sendImmediately: true
  // Result: status will be SENDING
}
```

---

## Example: Building Criteria from UI

```javascript
// User selects: Job > Job Name > Contains > "Healthcare"
const buildCriteria = (conditions) => {
  return {
    groups: [{
      logicalOperator: "AND",
      conditions: conditions.map(c => ({
        entityType: c.entity.toUpperCase(),  // "JOB"
        field: c.field,                       // "job_name"
        operator: c.operator,                 // "CONTAINS"
        value: c.value                        // "Healthcare"
      }))
    }],
    groupOperator: "AND"
  };
};
```

---

## Error Handling

```javascript
// NotFoundError when campaign doesn't exist
// ValueError when trying to refresh non-dynamic campaign
// Check for these in mutation responses
```
