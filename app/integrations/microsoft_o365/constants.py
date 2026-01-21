"""Microsoft O365 OAuth and Graph API constants."""

# Microsoft Identity Platform endpoints
MICROSOFT_AUTHORITY = "https://login.microsoftonline.com"
MICROSOFT_GRAPH_API = "https://graph.microsoft.com/v1.0"

# Multi-tenant: "common" allows users from any Microsoft tenant to authenticate
MICROSOFT_TENANT_ID = "common"

# OAuth 2.0 endpoints (using "common" for multi-tenant support)
AUTHORIZE_ENDPOINT = (
    f"{MICROSOFT_AUTHORITY}/{MICROSOFT_TENANT_ID}/oauth2/v2.0/authorize"
)
TOKEN_ENDPOINT = f"{MICROSOFT_AUTHORITY}/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token"

# Required scopes for O365 integration
O365_SCOPES = [
    "offline_access",  # Required for refresh token
    "User.Read",  # Read user profile
    "Mail.Send",  # Send mail as user
    "Calendars.Read",  # Read calendar events
    "Contacts.Read",  # Read user contacts
]
