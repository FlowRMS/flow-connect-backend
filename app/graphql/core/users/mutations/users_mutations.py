from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.core.users.services.user_service import UserService
from app.graphql.core.users.strawberry.user_input import UserInput
from app.graphql.core.users.strawberry.user_response import UserV2Response
from app.graphql.inject import inject


@strawberry.type
class UsersMutations:
    @strawberry.mutation
    @inject
    async def create_user(
        self,
        input: UserInput,
        service: Injected[UserService],
    ) -> UserV2Response:
        user = await service.create(input)
        return UserV2Response.from_orm_model(user)

    @strawberry.mutation
    @inject
    async def update_user(
        self,
        id: UUID,
        input: UserInput,
        service: Injected[UserService],
    ) -> UserV2Response:
        user = await service.update(id, input)
        return UserV2Response.from_orm_model(user)

    @strawberry.mutation
    @inject
    async def delete_user(
        self,
        id: UUID,
        service: Injected[UserService],
    ) -> bool:
        return await service.delete(id)
