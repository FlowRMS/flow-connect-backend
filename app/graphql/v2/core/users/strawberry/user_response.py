from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class UserLiteV2Response(DTOMixin[User]):
    _instance: strawberry.Private[User]
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: str
    full_name: str
    enabled: bool
    role: RbacRoleEnum
    auth_provider_id: str
    inside: bool | None
    outside: bool | None

    @classmethod
    def from_orm_model(cls, model: User) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            full_name=model.full_name,
            enabled=model.enabled,
            role=model.role,
            auth_provider_id=model.auth_provider_id,
            inside=model.inside,
            outside=model.outside,
        )


@strawberry.type
class UserV2Response(UserLiteV2Response):
    @strawberry.field
    async def supervisor(self) -> UserLiteV2Response | None:
        supervisor = await self._instance.awaitable_attrs.supervisor
        return UserLiteV2Response.from_orm_model_optional(supervisor)
