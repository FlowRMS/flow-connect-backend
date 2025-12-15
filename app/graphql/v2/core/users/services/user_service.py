from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.users.models.user import UserV2
from app.graphql.v2.core.users.repositories.users_repository import UsersRepository
from app.graphql.v2.core.users.strawberry.user_input import UserInput


class UserService:
    def __init__(
        self,
        repository: UsersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, user_id: UUID) -> UserV2:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return user

    async def get_by_email(self, email: str) -> UserV2 | None:
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> UserV2 | None:
        return await self.repository.get_by_username(username)

    async def get_by_keycloak_id(self, auth_provider_id: str) -> UserV2 | None:
        return await self.repository.get_by_keycloak_id(auth_provider_id)

    async def create(self, user_input: UserInput) -> UserV2:
        return await self.repository.create(user_input.to_orm_model())

    async def update(self, user_id: UUID, user_input: UserInput) -> UserV2:
        user = user_input.to_orm_model()
        user.id = user_id
        return await self.repository.update(user)

    async def delete(self, user_id: UUID) -> bool:
        if not await self.repository.exists(user_id):
            raise NotFoundError(f"User with id {user_id} not found")
        return await self.repository.delete(user_id)

    async def search_users(
        self, search_term: str, enabled: bool | None = True, limit: int = 20
    ) -> list[UserV2]:
        return await self.repository.search_by_name(search_term, enabled, limit)

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[UserV2]:
        return await self.repository.list_all(limit, offset)
