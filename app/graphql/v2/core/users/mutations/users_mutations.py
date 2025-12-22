from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.users.services.user_service import UserService
from app.graphql.v2.core.users.strawberry.user_input import UserInput
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class UsersMutations:
    @strawberry.mutation
    @inject
    async def create_user(
        self,
        input: UserInput,
        service: Injected[UserService],
    ) -> UserResponse:
        user = await service.create(input)
        return UserResponse.from_orm_model(user)

    @strawberry.mutation
    @inject
    async def update_user(
        self,
        id: UUID,
        input: UserInput,
        service: Injected[UserService],
    ) -> UserResponse:
        user = await service.update(id, input)
        return UserResponse.from_orm_model(user)

    @strawberry.mutation
    @inject
    async def delete_user(
        self,
        id: UUID,
        service: Injected[UserService],
    ) -> bool:
        return await service.delete(id)
