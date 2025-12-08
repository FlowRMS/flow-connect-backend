"""GraphQL queries for O365 integration."""

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.integrations.types import O365ConnectionStatusType
from app.integrations.microsoft_o365.services.o365_auth_service import O365AuthService


@strawberry.type
class O365Queries:
    """GraphQL queries for O365 integration."""

    @strawberry.field
    @inject
    async def o365_auth_url(
        self,
        service: Injected[O365AuthService],
        state: str | None = None,
    ) -> str:
        """
        Get OAuth authorization URL for Microsoft O365.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        return service.get_authorization_url(state)

    @strawberry.field
    @inject
    async def o365_connection_status(
        self,
        service: Injected[O365AuthService],
    ) -> O365ConnectionStatusType:
        """Check current user's O365 connection status."""
        status = await service.get_connection_status()
        return O365ConnectionStatusType(
            is_connected=status.is_connected,
            microsoft_email=status.microsoft_email,
            expires_at=status.expires_at,
            last_used_at=status.last_used_at,
        )
