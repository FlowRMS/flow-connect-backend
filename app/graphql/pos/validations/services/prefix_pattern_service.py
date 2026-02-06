import uuid

from commons.auth import AuthInfo

from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.pos.validations.exceptions import (
    PrefixPatternDuplicateError,
    PrefixPatternNotFoundError,
    UserNotAuthenticatedError,
)
from app.graphql.pos.validations.models import PrefixPattern
from app.graphql.pos.validations.repositories import PrefixPatternRepository


class PrefixPatternService:
    def __init__(
        self,
        repository: PrefixPatternRepository,
        user_org_repository: UserOrgRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.user_org_repository = user_org_repository
        self.auth_info = auth_info

    async def _get_user_org_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise UserNotAuthenticatedError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    async def create_pattern(
        self,
        name: str,
        description: str | None = None,
    ) -> PrefixPattern:
        user_org_id = await self._get_user_org_id()

        if await self.repository.exists_by_org_and_name(user_org_id, name):
            raise PrefixPatternDuplicateError(f"Pattern '{name}' already exists")

        pattern = PrefixPattern(
            organization_id=user_org_id,
            name=name,
            description=description,
        )
        pattern.created_by_id = self.auth_info.flow_user_id

        return await self.repository.create(pattern)

    async def get_all_patterns(self) -> list[PrefixPattern]:
        user_org_id = await self._get_user_org_id()
        return await self.repository.get_all_by_org(user_org_id)

    async def delete_pattern(self, pattern_id: uuid.UUID) -> bool:
        user_org_id = await self._get_user_org_id()
        existing = await self.repository.get_by_id(pattern_id)

        if existing is None or existing.organization_id != user_org_id:
            raise PrefixPatternNotFoundError(f"Pattern {pattern_id} not found")

        return await self.repository.delete(pattern_id)
