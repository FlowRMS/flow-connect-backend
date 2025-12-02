"""Service for Users entity business logic."""

from commons.auth import AuthInfo
from commons.db.models import User

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

    async def search_users(self, search_term: str, limit: int = 20) -> list[User]:
        """
        Search users by name or email.

        Args:
            search_term: The search term to match against user names or email
            limit: Maximum number of users to return (default: 20)

        Returns:
            List of User objects matching the search criteria
        """
        return await self.repository.search_by_name(search_term, limit)
