# Microsoft O365 Integration

This module enables users to connect their Microsoft 365 account to send emails on their behalf.

## OAuth Flow Overview

```
┌──────────┐     1. Get Auth URL      ┌──────────┐
│ Frontend │ ───────────────────────► │ Backend  │
│          │ ◄─────────────────────── │ GraphQL  │
│          │     Returns URL          │          │
└────┬─────┘                          └──────────┘
     │
     │ 2. Redirect user to Microsoft
     ▼
┌──────────────────┐
│ Microsoft Login  │
│ (User consents)  │
└────────┬─────────┘
         │
         │ 3. Redirect to callback with ?code=xxx
         ▼
┌──────────────────────────────────────┐
│ Backend: /api/integrations/o365/callback │
│ Redirects to frontend with code     │
└────────┬─────────────────────────────┘
         │
         │ 4. Frontend receives code
         ▼
┌──────────┐     5. Exchange code     ┌──────────┐
│ Frontend │ ───────────────────────► │ Backend  │
│          │     (o365Connect)        │ GraphQL  │
│          │ ◄─────────────────────── │          │
│          │     Returns success      │          │
└──────────┘                          └──────────┘
```

## GraphQL API

### Queries

#### Get Authorization URL

```graphql
query GetO365AuthUrl($state: String) {
  o365AuthUrl(state: $state)
}
```

**Response:**
```json
{
  "data": {
    "o365AuthUrl": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=xxx&response_type=code&redirect_uri=xxx&scope=offline_access%20User.Read%20Mail.Send&state=xxx"
  }
}
```

#### Check Connection Status

```graphql
query GetO365ConnectionStatus {
  o365ConnectionStatus {
    isConnected
    microsoftEmail
    expiresAt
    lastUsedAt
  }
}
```

**Response (connected):**
```json
{
  "data": {
    "o365ConnectionStatus": {
      "isConnected": true,
      "microsoftEmail": "user@company.com",
      "expiresAt": "2024-12-07T12:00:00Z",
      "lastUsedAt": "2024-12-07T10:30:00Z"
    }
  }
}
```

**Response (not connected):**
```json
{
  "data": {
    "o365ConnectionStatus": {
      "isConnected": false,
      "microsoftEmail": null,
      "expiresAt": null,
      "lastUsedAt": null
    }
  }
}
```

### Mutations

#### Connect (Exchange Code for Token)

```graphql
mutation O365Connect($code: String!) {
  o365Connect(code: $code) {
    success
    microsoftEmail
    error
  }
}
```

**Response (success):**
```json
{
  "data": {
    "o365Connect": {
      "success": true,
      "microsoftEmail": "user@company.com",
      "error": null
    }
  }
}
```

**Response (failure):**
```json
{
  "data": {
    "o365Connect": {
      "success": false,
      "microsoftEmail": null,
      "error": "Authorization code expired"
    }
  }
}
```

#### Disconnect

```graphql
mutation O365Disconnect {
  o365Disconnect
}
```

**Response:**
```json
{
  "data": {
    "o365Disconnect": true
  }
}
```

#### Send Email

```graphql
mutation O365SendEmail($input: O365SendEmailInput!) {
  o365SendEmail(input: $input) {
    success
    messageId
    error
  }
}
```

**Input:**
```graphql
input O365SendEmailInput {
  to: [String!]!
  subject: String!
  body: String!
  bodyType: String = "HTML"  # "HTML" or "Text"
  cc: [String!]
  bcc: [String!]
}
```

**Example:**
```json
{
  "input": {
    "to": ["recipient@example.com"],
    "subject": "Hello from Flow CRM",
    "body": "<h1>Hello!</h1><p>This is a test email.</p>",
    "bodyType": "HTML",
    "cc": ["cc@example.com"]
  }
}
```

**Response:**
```json
{
  "data": {
    "o365SendEmail": {
      "success": true,
      "messageId": null,
      "error": null
    }
  }
}
```

## Frontend Implementation

### 1. Settings Page - Connection Status

```typescript
// Check if user is connected
const { data } = await client.query({
  query: GET_O365_CONNECTION_STATUS
});

if (data.o365ConnectionStatus.isConnected) {
  // Show connected state with email
  showConnectedUI(data.o365ConnectionStatus.microsoftEmail);
} else {
  // Show "Connect" button
  showConnectButton();
}
```

### 2. Initiate OAuth Flow

```typescript
async function connectO365() {
  // Generate a random state for CSRF protection
  const state = crypto.randomUUID();
  sessionStorage.setItem('o365_oauth_state', state);

  // Get the authorization URL
  const { data } = await client.query({
    query: GET_O365_AUTH_URL,
    variables: { state }
  });

  // Redirect user to Microsoft login
  window.location.href = data.o365AuthUrl;
}
```

### 3. Handle OAuth Callback

After Microsoft authentication, the user is redirected to:
```
/settings/integrations/o365?code=xxx&state=xxx
```

Or on error:
```
/settings/integrations/o365?error=access_denied&error_description=User%20cancelled
```

```typescript
// On the callback page (/settings/integrations/o365)
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');
  const state = params.get('state');
  const error = params.get('error');

  if (error) {
    showError(params.get('error_description') || error);
    return;
  }

  if (code) {
    // Verify state matches (CSRF protection)
    const savedState = sessionStorage.getItem('o365_oauth_state');
    if (state !== savedState) {
      showError('Invalid state parameter');
      return;
    }

    // Exchange code for token
    exchangeCode(code);
  }
}, []);

async function exchangeCode(code: string) {
  const { data } = await client.mutate({
    mutation: O365_CONNECT,
    variables: { code }
  });

  if (data.o365Connect.success) {
    showSuccess(`Connected as ${data.o365Connect.microsoftEmail}`);
    // Clean up URL
    window.history.replaceState({}, '', '/settings/integrations/o365');
  } else {
    showError(data.o365Connect.error);
  }
}
```

### 4. Disconnect

```typescript
async function disconnectO365() {
  const { data } = await client.mutate({
    mutation: O365_DISCONNECT
  });

  if (data.o365Disconnect) {
    showSuccess('Disconnected from Microsoft 365');
  }
}
```

### 5. Send Email

```typescript
async function sendEmail(to: string[], subject: string, body: string) {
  const { data } = await client.mutate({
    mutation: O365_SEND_EMAIL,
    variables: {
      input: {
        to,
        subject,
        body,
        bodyType: 'HTML'
      }
    }
  });

  if (data.o365SendEmail.success) {
    showSuccess('Email sent!');
  } else {
    showError(data.o365SendEmail.error);
  }
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `No active O365 token found` | User not connected | Prompt user to connect |
| `Token refresh failed` | Refresh token expired/revoked | Prompt user to reconnect |
| `Authorization code expired` | Code not exchanged in time | Restart OAuth flow |
| `access_denied` | User cancelled consent | Show friendly message |

## Security Notes

1. **State Parameter**: Always use a random state parameter and verify it on callback to prevent CSRF attacks
2. **Token Storage**: Tokens are stored securely in the database, never exposed to frontend
3. **Auto-Refresh**: Access tokens are automatically refreshed when expired (refresh tokens last ~90 days)
4. **Scope**: Only `Mail.Send` and `User.Read` permissions are requested (minimal scope)
