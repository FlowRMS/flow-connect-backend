# Gmail Integration

This module enables users to connect their Gmail account to send emails on their behalf.

## OAuth Flow Overview

```
┌──────────┐     1. Get Auth URL      ┌──────────┐
│ Frontend │ ───────────────────────► │ Backend  │
│          │ ◄─────────────────────── │ GraphQL  │
│          │     Returns URL          │          │
└────┬─────┘                          └──────────┘
     │
     │ 2. Redirect user to Google
     ▼
┌──────────────────┐
│  Google Login    │
│ (User consents)  │
└────────┬─────────┘
         │
         │ 3. Redirect to callback with ?code=xxx
         ▼
┌──────────────────────────────────────┐
│ Backend: /api/integrations/gmail/callback │
│ Redirects to frontend with code     │
└────────┬─────────────────────────────┘
         │
         │ 4. Frontend receives code
         ▼
┌──────────┐     5. Exchange code     ┌──────────┐
│ Frontend │ ───────────────────────► │ Backend  │
│          │     (gmailConnect)       │ GraphQL  │
│          │ ◄─────────────────────── │          │
│          │     Returns success      │          │
└──────────┘                          └──────────┘
```

## Google Cloud Console Setup

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)

2. **Create a project** (or select existing)

3. **Enable Gmail API**
   - APIs & Services → Library → Search "Gmail API" → Enable

4. **Configure OAuth Consent Screen**
   - APIs & Services → OAuth consent screen
   - User Type: **External** (for multi-tenant)
   - Add scopes:
     - `openid`
     - `.../auth/userinfo.email`
     - `.../auth/gmail.send`

5. **Create OAuth Credentials**
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Web application**
   - Authorized redirect URIs: `https://yourapp.com/api/integrations/gmail/callback`
   - Copy **Client ID** and **Client Secret**

## GraphQL API

### Queries

#### Get Authorization URL

```graphql
query GetGmailAuthUrl($state: String) {
  gmailAuthUrl(state: $state)
}
```

**Response:**
```json
{
  "data": {
    "gmailAuthUrl": "https://accounts.google.com/o/oauth2/v2/auth?client_id=xxx&response_type=code&redirect_uri=xxx&scope=openid%20..."
  }
}
```

#### Check Connection Status

```graphql
query GetGmailConnectionStatus {
  gmailConnectionStatus {
    isConnected
    googleEmail
    expiresAt
    lastUsedAt
  }
}
```

**Response (connected):**
```json
{
  "data": {
    "gmailConnectionStatus": {
      "isConnected": true,
      "googleEmail": "user@gmail.com",
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
    "gmailConnectionStatus": {
      "isConnected": false,
      "googleEmail": null,
      "expiresAt": null,
      "lastUsedAt": null
    }
  }
}
```

### Mutations

#### Connect (Exchange Code for Token)

```graphql
mutation GmailConnect($code: String!) {
  gmailConnect(code: $code) {
    success
    googleEmail
    error
  }
}
```

**Response (success):**
```json
{
  "data": {
    "gmailConnect": {
      "success": true,
      "googleEmail": "user@gmail.com",
      "error": null
    }
  }
}
```

**Response (failure):**
```json
{
  "data": {
    "gmailConnect": {
      "success": false,
      "googleEmail": null,
      "error": "Authorization code expired"
    }
  }
}
```

#### Disconnect

```graphql
mutation GmailDisconnect {
  gmailDisconnect
}
```

**Response:**
```json
{
  "data": {
    "gmailDisconnect": true
  }
}
```

#### Send Email

```graphql
mutation GmailSendEmail($input: GmailSendEmailInput!) {
  gmailSendEmail(input: $input) {
    success
    messageId
    error
  }
}
```

**Input:**
```graphql
input GmailSendEmailInput {
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
    "gmailSendEmail": {
      "success": true,
      "messageId": "18c1234567890abc",
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
  query: GET_GMAIL_CONNECTION_STATUS
});

if (data.gmailConnectionStatus.isConnected) {
  // Show connected state with email
  showConnectedUI(data.gmailConnectionStatus.googleEmail);
} else {
  // Show "Connect" button
  showConnectButton();
}
```

### 2. Initiate OAuth Flow

```typescript
async function connectGmail() {
  // Generate a random state for CSRF protection
  const state = crypto.randomUUID();
  sessionStorage.setItem('gmail_oauth_state', state);

  // Get the authorization URL
  const { data } = await client.query({
    query: GET_GMAIL_AUTH_URL,
    variables: { state }
  });

  // Redirect user to Google login
  window.location.href = data.gmailAuthUrl;
}
```

### 3. Handle OAuth Callback

After Google authentication, the user is redirected to:
```
/settings/integrations/gmail?code=xxx&state=xxx
```

Or on error:
```
/settings/integrations/gmail?error=access_denied
```

```typescript
// On the callback page (/settings/integrations/gmail)
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const code = params.get('code');
  const state = params.get('state');
  const error = params.get('error');

  if (error) {
    showError(error);
    return;
  }

  if (code) {
    // Verify state matches (CSRF protection)
    const savedState = sessionStorage.getItem('gmail_oauth_state');
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
    mutation: GMAIL_CONNECT,
    variables: { code }
  });

  if (data.gmailConnect.success) {
    showSuccess(`Connected as ${data.gmailConnect.googleEmail}`);
    // Clean up URL
    window.history.replaceState({}, '', '/settings/integrations/gmail');
  } else {
    showError(data.gmailConnect.error);
  }
}
```

### 4. Disconnect

```typescript
async function disconnectGmail() {
  const { data } = await client.mutate({
    mutation: GMAIL_DISCONNECT
  });

  if (data.gmailDisconnect) {
    showSuccess('Disconnected from Gmail');
  }
}
```

### 5. Send Email

```typescript
async function sendEmail(to: string[], subject: string, body: string) {
  const { data } = await client.mutate({
    mutation: GMAIL_SEND_EMAIL,
    variables: {
      input: {
        to,
        subject,
        body,
        bodyType: 'HTML'
      }
    }
  });

  if (data.gmailSendEmail.success) {
    showSuccess('Email sent!');
  } else {
    showError(data.gmailSendEmail.error);
  }
}
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `No active Gmail token found` | User not connected | Prompt user to connect |
| `Token refresh failed` | Refresh token expired/revoked | Prompt user to reconnect |
| `Authorization code expired` | Code not exchanged in time | Restart OAuth flow |
| `access_denied` | User cancelled consent | Show friendly message |

## Security Notes

1. **State Parameter**: Always use a random state parameter and verify it on callback to prevent CSRF attacks
2. **Token Storage**: Tokens are stored securely in the database, never exposed to frontend
3. **Auto-Refresh**: Access tokens are automatically refreshed when expired
4. **Scope Limitation**: Only `gmail.send` and `userinfo.email` permissions are requested (minimal scope)
5. **Prompt Consent**: We use `prompt=consent` to ensure we always get a refresh token

## Environment Variables

```env
GMAIL_CLIENT_ID=xxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxx
GMAIL_REDIRECT_URI=https://yourapp.com/api/integrations/gmail/callback
```
