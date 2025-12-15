from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.core.users.models.user import UserV2


class UsersRepository(BaseRepository[UserV2]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, UserV2)

    async def get_by_email(self, email: str) -> UserV2 | None:
        stmt = select(UserV2).where(UserV2.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserV2 | None:
        stmt = select(UserV2).where(UserV2.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_keycloak_id(self, auth_provider_id: str) -> UserV2 | None:
        stmt = select(UserV2).where(UserV2.auth_provider_id == auth_provider_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self, search_term: str, enabled: bool | None = True, limit: int = 20
    ) -> list[UserV2]:
        stmt = (
            select(UserV2)
            .where(
                (UserV2.first_name.ilike(f"%{search_term}%"))
                | (UserV2.last_name.ilike(f"%{search_term}%"))
                | (UserV2.email.ilike(f"%{search_term}%"))
            )
            .limit(limit)
        )

        if enabled is not None:
            stmt = stmt.where(UserV2.enabled == enabled)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
