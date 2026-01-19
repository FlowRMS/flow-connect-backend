import uuid
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.user import User
from loguru import logger

from app.auth.models import AuthUser, AuthUserInput
from app.auth.workos_auth_service import WorkOSAuthService
from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.users.repositories.users_repository import UsersRepository
from app.graphql.v2.core.users.strawberry.user_input import UserInput


class UserService:
    def __init__(
        self,
        repository: UsersRepository,
        auth_info: AuthInfo,
        workos_auth_service: WorkOSAuthService,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info
        self.workos_auth_service = workos_auth_service

    async def get_by_id(self, user_id: UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)

    async def get_by_auth_provider_id(self, auth_provider_id: str) -> User | None:
        return await self.repository.get_by_keycloak_id(auth_provider_id)

    async def create(self, user_input: UserInput) -> User:
        existing_user = await self.repository.get_by_email(user_input.email)
        if existing_user:
            raise ValueError(f"User with email {user_input.email} already exists")

        user_model = user_input.to_orm_model()
        auth_user = await self._create_workos_user(user_input)
        if not auth_user:
            raise Exception("Failed to create user in WorkOS")

        user_model.auth_provider_id = auth_user.id
        user_model.id = auth_user.external_id
        return await self.repository.create(user_model)

    async def _create_workos_user(
        self, user_input: UserInput, external_id: uuid.UUID | None = None
    ) -> AuthUser | None:
        auth_input = AuthUserInput(
            email=user_input.email,
            external_id=uuid.uuid4() if external_id is None else external_id,
            tenant_id=self.auth_info.tenant_id,
            role=user_input.role,
            first_name=user_input.first_name,
            last_name=user_input.last_name,
            email_verified=False,
            metadata={
                "enabled": str(user_input.enabled),
            },
        )
        auth_user = await self.workos_auth_service.create_user(auth_input)
        if not auth_user:
            logger.warning(f"Failed to create WorkOS user for {user_input.email}")
        return auth_user

    async def update(self, user_id: UUID, user_input: UserInput) -> User:
        user = user_input.to_orm_model()
        user.id = user_id
        await self._update_workos_user(user_input)
        return await self.repository.update(user)

    async def _update_workos_user(self, user_input: UserInput) -> None:
        user = await self.repository.get_by_username(user_input.username)
        if not user or not user.auth_provider_id:
            raise NotFoundError(
                f"User with username {user_input.username} not found in WorkOS"
            )

        workos_user = await self.workos_auth_service.get_user(user.auth_provider_id)

        if not workos_user:
            raise NotFoundError(
                f"User with auth provider id {user.auth_provider_id} not found in WorkOS"
            )

        if workos_user.external_id != user.id:
            raise ValueError("Mismatch between local user ID and WorkOS external ID")

        auth_input = AuthUserInput(
            email=user_input.email,
            tenant_id=self.auth_info.tenant_name,
            role=user_input.role,
            first_name=user_input.first_name,
            last_name=user_input.last_name,
            external_id=user.id,
            metadata={
                "enabled": str(user_input.enabled),
            },
        )
        _ = await self.workos_auth_service.update_user(
            user.auth_provider_id, auth_input
        )

    async def delete(self, user_id: UUID) -> bool:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        if self.workos_auth_service and user.auth_provider_id:
            _ = await self.workos_auth_service.delete_user(user.auth_provider_id)
        return await self.repository.delete(user_id)

    async def search_users(
        self,
        search_term: str,
        enabled: bool | None = True,
        is_inside: bool | None = None,
        is_outside: bool | None = None,
        limit: int = 20,
    ) -> list[User]:
        return await self.repository.search_by_name(
            search_term, enabled, is_inside, is_outside, limit
        )

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[User]:
        return await self.repository.list_users(limit, offset)
