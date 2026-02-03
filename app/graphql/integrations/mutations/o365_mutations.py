import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.integrations.o365_types import (
    O365ConnectionResultType,
    O365SendEmailInput,
    O365SendEmailResultType,
)
from app.integrations.microsoft_o365.services.o365_auth_service import (
    O365AuthError,
    O365AuthService,
)


@strawberry.type
class O365Mutations:
    """GraphQL mutations for O365 integration."""

    @strawberry.mutation
    @inject
    async def o365_connect(
        self,
        code: str,
        service: Injected[O365AuthService],
    ) -> O365ConnectionResultType:
        """
        Complete OAuth flow with authorization code.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            O365ConnectionResultType with success status and email or error
        """
        try:
            token = await service.exchange_code_for_token(code)
            return O365ConnectionResultType(
                success=True,
                microsoft_email=token.microsoft_email,
            )
        except O365AuthError as e:
            return O365ConnectionResultType(
                success=False,
                error=str(e),
            )

    @strawberry.mutation
    @inject
    async def o365_disconnect(
        self,
        service: Injected[O365AuthService],
    ) -> bool:
        """
        Revoke O365 integration for current user.

        Returns:
            True if disconnected successfully, False if no connection found
        """
        return await service.revoke_access()

    @strawberry.mutation
    @inject
    async def o365_send_email(
        self,
        input: O365SendEmailInput,
        service: Injected[O365AuthService],
    ) -> O365SendEmailResultType:
        """
        Send email via user's O365 account.

        Args:
            input: Email details (to, subject, body, etc.)

        Returns:
            O365SendEmailResultType with success status and optional error
        """
        result = await service.send_email(
            to=input.to,
            subject=input.subject,
            body=input.body,
            body_type=input.body_type,
            cc=input.cc,
            bcc=input.bcc,
        )
        return O365SendEmailResultType(
            success=result.success,
            message_id=result.message_id,
            error=result.error,
        )
