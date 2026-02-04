import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.integrations.gmail_types import (
    GmailConnectionResultType,
    GmailSendEmailInput,
    GmailSendEmailResultType,
)
from app.integrations.gmail.services.gmail_auth_service import GmailAuthService
from app.integrations.gmail.services.gmail_types import GmailAuthError


@strawberry.type
class GmailMutations:
    """GraphQL mutations for Gmail integration."""

    @strawberry.mutation
    @inject
    async def gmail_connect(
        self,
        code: str,
        service: Injected[GmailAuthService],
    ) -> GmailConnectionResultType:
        """
        Complete OAuth flow with authorization code.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            GmailConnectionResultType with success status and email or error
        """
        try:
            token = await service.exchange_code_for_token(code)
            return GmailConnectionResultType(
                success=True,
                google_email=token.google_email,
            )
        except GmailAuthError as e:
            return GmailConnectionResultType(
                success=False,
                error=str(e),
            )

    @strawberry.mutation
    @inject
    async def gmail_disconnect(
        self,
        service: Injected[GmailAuthService],
    ) -> bool:
        """
        Revoke Gmail integration for current user.

        Returns:
            True if disconnected successfully, False if no connection found
        """
        return await service.revoke_access()

    @strawberry.mutation
    @inject
    async def gmail_send_email(
        self,
        input: GmailSendEmailInput,
        service: Injected[GmailAuthService],
    ) -> GmailSendEmailResultType:
        """
        Send email via user's Gmail account.

        Args:
            input: Email details (to, subject, body, etc.)

        Returns:
            GmailSendEmailResultType with success status and optional error
        """
        result = await service.send_email(
            to=input.to,
            subject=input.subject,
            body=input.body,
            body_type=input.body_type,
            cc=input.cc,
            bcc=input.bcc,
        )
        return GmailSendEmailResultType(
            success=result.success,
            message_id=result.message_id,
            error=result.error,
        )
