"""Repository for O365 user token operations."""

import uuid
from datetime import datetime

import pendulum
from commons.db.v6.crm import O365UserToken
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class O365TokenRepository(BaseRepository[O365UserToken]):
    """Repository for O365 user token CRUD operations."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, O365UserToken)

    async def get_by_user_id(self, user_id: uuid.UUID) -> O365UserToken | None:
        """
        Get token for a specific user.

        Args:
            user_id: The user's ID

        Returns:
            The token entity if found, None otherwise
        """
        result = await self.session.execute(
            select(O365UserToken).where(O365UserToken.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active_token(self, user_id: uuid.UUID) -> O365UserToken | None:
        """
        Get active, non-expired token for user.

        Args:
            user_id: The user's ID

        Returns:
            Active token if found and not expired, None otherwise
        """
        result = await self.session.execute(
            select(O365UserToken).where(
                O365UserToken.user_id == user_id,
                O365UserToken.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def upsert_token(
        self,
        user_id: uuid.UUID,
        microsoft_user_id: str,
        microsoft_email: str,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        scope: str,
        token_type: str = "Bearer",
    ) -> O365UserToken:
        """
        Create or update token for user.

        Args:
            user_id: The user's ID
            microsoft_user_id: Microsoft user OID
            microsoft_email: Microsoft email/UPN
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_at: Token expiration time
            scope: Space-separated scopes
            token_type: Token type (default: Bearer)

        Returns:
            Created or updated token entity
        """
        existing = await self.get_by_user_id(user_id)

        if existing:
            existing.microsoft_user_id = microsoft_user_id
            existing.microsoft_email = microsoft_email
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.token_type = token_type
            existing.expires_at = expires_at
            existing.scope = scope
            existing.is_active = True

            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        token = O365UserToken(
            user_id=user_id,
            microsoft_user_id=microsoft_user_id,
            microsoft_email=microsoft_email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_at=expires_at,
            scope=scope,
            is_active=True,
        )
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def deactivate_token(self, user_id: uuid.UUID) -> bool:
        """
        Soft-delete/deactivate user's token.

        Args:
            user_id: The user's ID

        Returns:
            True if token was deactivated, False if no token found
        """
        result = await self.session.execute(
            update(O365UserToken)
            .where(O365UserToken.user_id == user_id)
            .values(is_active=False)
        )
        await self.session.flush()
        return result.rowcount > 0  # type: ignore[union-attr]

    async def update_last_used(self, token_id: uuid.UUID) -> None:
        """
        Update last_used_at timestamp.

        Args:
            token_id: The token's ID
        """
        _ = await self.session.execute(
            update(O365UserToken)
            .where(O365UserToken.id == token_id)
            .values(last_used_at=pendulum.now(tz="UTC"))
        )
        await self.session.flush()

    async def update_tokens(
        self,
        token_id: uuid.UUID,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
    ) -> O365UserToken:
        """
        Update tokens after refresh.

        Args:
            token_id: The token entity ID
            access_token: New access token
            refresh_token: New refresh token
            expires_at: New expiration time

        Returns:
            Updated token entity
        """
        _ = await self.session.execute(
            update(O365UserToken)
            .where(O365UserToken.id == token_id)
            .values(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
        )
        await self.session.flush()

        result = await self.session.execute(
            select(O365UserToken).where(O365UserToken.id == token_id)
        )
        token = result.scalar_one()
        await self.session.refresh(token)
        return token
