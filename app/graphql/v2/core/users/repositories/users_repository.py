from commons.db.v6.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class UsersRepository(BaseRepository[User]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_keycloak_id(self, auth_provider_id: str) -> User | None:
        stmt = select(User).where(User.auth_provider_id == auth_provider_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        search_term: str,
        enabled: bool | None = True,
        is_inside: bool | None = None,
        is_outside: bool | None = None,
        limit: int = 20,
    ) -> list[User]:
        stmt = (
            select(User)
            .where(
                (User.first_name.ilike(f"%{search_term}%"))
                | (User.last_name.ilike(f"%{search_term}%"))
                | (User.email.ilike(f"%{search_term}%"))
            )
            .limit(limit)
        )

        if enabled is not None:
            stmt = stmt.where(User.enabled == enabled)

        if is_inside is not None and is_inside:
            stmt = stmt.where(User.inside == is_inside)

        if is_outside is not None and is_outside:
            stmt = stmt.where(User.outside == is_outside)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
