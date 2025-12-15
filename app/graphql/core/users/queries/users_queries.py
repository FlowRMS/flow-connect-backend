from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.core.users.services.user_service import UserService
from app.graphql.core.users.strawberry.user_response import UserV2Response
from app.graphql.inject import inject


@strawberry.type
class UsersQueries:
    @strawberry.field
    @inject
    async def user(
        self,
        service: Injected[UserService],
        id: UUID,
    ) -> UserV2Response:
        user = await service.get_by_id(id)
        return UserV2Response.from_orm_model(user)

    @strawberry.field
    @inject
    async def user_search(
        self,
        service: Injected[UserService],
        search_term: str,
        enabled: bool | None = True,
        limit: int = 20,
    ) -> list[UserV2Response]:
        return UserV2Response.from_orm_model_list(
            await service.search_users(search_term, enabled, limit)
        )

    @strawberry.field
    @inject
    async def users(
        self,
        service: Injected[UserService],
        limit: int | None = None,
        offset: int = 0,
    ) -> list[UserV2Response]:
        return UserV2Response.from_orm_model_list(await service.list_all(limit, offset))
