import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.integrations.gmail_types import GmailConnectionStatusType
from app.integrations.gmail.services.gmail_auth_service import GmailAuthService


@strawberry.type
class GmailQueries:
    """GraphQL queries for Gmail integration."""

    @strawberry.field
    @inject
    async def gmail_auth_url(
        self,
        service: Injected[GmailAuthService],
        state: str | None = None,
    ) -> str:
        """
        Get OAuth authorization URL for Gmail.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        return service.get_authorization_url(state)

    @strawberry.field
    @inject
    async def gmail_connection_status(
        self,
        service: Injected[GmailAuthService],
    ) -> GmailConnectionStatusType:
        """Check current user's Gmail connection status."""
        status = await service.get_connection_status()
        return GmailConnectionStatusType(
            is_connected=status.is_connected,
            google_email=status.google_email,
            expires_at=status.expires_at,
            last_used_at=status.last_used_at,
        )
