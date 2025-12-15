from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.models.user import UserV2


@strawberry.type
class UserLiteV2Response(DTOMixin[UserV2]):
    _instance: strawberry.Private[UserV2]
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    full_name: str
    enabled: bool
    role_id: UUID
    auth_provider_id: str
    inside: bool | None
    outside: bool | None
    supervisor_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: UserV2) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            full_name=model.full_name,
            enabled=model.enabled,
            role_id=model.role_id,
            auth_provider_id=model.auth_provider_id,
            inside=model.inside,
            outside=model.outside,
            supervisor_id=model.supervisor_id,
        )


@strawberry.type
class UserV2Response(UserLiteV2Response):
    @strawberry.field
    async def supervisor(self) -> UserLiteV2Response | None:
        supervisor = await self._instance.awaitable_attrs.supervisor
        return UserLiteV2Response.from_orm_model_optional(supervisor)
