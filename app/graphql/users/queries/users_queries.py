"""GraphQL queries for Users entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.users.services.users_service import UsersService
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class UsersQueries:
    """GraphQL queries for Users entity."""

    @strawberry.field
    @inject
    async def user(
        self,
        id: UUID,
        service: Injected[UsersService],
    ) -> UserResponse:
        """Get a user by ID."""
        return UserResponse.from_orm_model(await service.get_user(id))

    @strawberry.field
    @inject
    async def user_search(
        self,
        service: Injected[UsersService],
        search_term: str,
        limit: int = 20,
    ) -> list[UserResponse]:
        """
        Search users by name or email.

        Args:
            search_term: The search term to match against user names or email
            limit: Maximum number of users to return (default: 20)

        Returns:
            List of UserResponse objects matching the search criteria
        """
        return UserResponse.from_orm_model_list(
            await service.search_users(search_term, limit)
        )
