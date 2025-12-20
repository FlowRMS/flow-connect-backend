"""Service for Users entity business logic."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import User

from app.errors.common_errors import NotFoundError
from app.graphql.users.repositories.users_repository import UsersRepository


class UsersService:
    """Service for Users entity business logic."""

    def __init__(
        self,
        repository: UsersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_user(self, user_id: UUID) -> User:
        """
        Get a user by ID.

        Args:
            user_id: The user ID to find

        Returns:
            The user entity

        Raises:
            NotFoundError: If the user doesn't exist
        """
        user = await self.repository.find_by_id(user_id)
        if not user:
            raise NotFoundError(str(user_id))
        return user

    async def search_users(
        self,
        search_term: str,
        limit: int = 20,
        is_inside: bool | None = None,
        is_outside: bool | None = None,
    ) -> list[User]:
        """
        Search users by name or email.

        Args:
            search_term: The search term to match against user names or email
            limit: Maximum number of users to return (default: 20)

        Returns:
            List of User objects matching the search criteria
        """
        return await self.repository.search_by_name(
            search_term, limit, is_inside, is_outside
        )
