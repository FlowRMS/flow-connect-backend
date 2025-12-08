"""Repository for Users entity."""

from uuid import UUID

from commons.db.models import User
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class UsersRepository(BaseRepository[User]):
    """Repository for Users entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, User)

    async def find_by_id(self, user_id: UUID) -> User | None:
        """
        Find a user by ID.

        Args:
            user_id: The user ID to find

        Returns:
            User if found, None otherwise
        """
        return await self.get_by_id(user_id)

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[User]:
        """
        Search users by first name, last name, or email using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against user names or email
            limit: Maximum number of users to return (default: 20)

        Returns:
            List of User objects matching the search criteria
        """
        stmt = (
            select(User)
            .where(
                or_(
                    User.first_name.ilike(f"%{search_term}%"),
                    User.last_name.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%"),
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
