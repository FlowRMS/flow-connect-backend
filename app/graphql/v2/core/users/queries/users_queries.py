from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.users.services.user_service import UserService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class UsersQueries:
    @strawberry.field
    @inject
    async def user(
        self,
        service: Injected[UserService],
        id: UUID,
    ) -> UserResponse:
        user = await service.get_by_id(id)
        return UserResponse.from_orm_model(user)

    @strawberry.field
    @inject
    async def user_search(
        self,
        service: Injected[UserService],
        search_term: str,
        enabled: bool | None = True,
        limit: int = 20,
    ) -> list[UserResponse]:
        return UserResponse.from_orm_model_list(
            await service.search_users(search_term, enabled, limit)
        )

    @strawberry.field
    @inject
    async def users(
        self,
        service: Injected[UserService],
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UserResponse]:
        return UserResponse.from_orm_model_list(await service.list_all(limit, offset))
