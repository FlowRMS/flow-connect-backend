from typing import Any, override

import strawberry
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from strawberry import BasePermission

from app.core.context import Context


class RolePermissionAccess(BasePermission):
    message = "You do not have permission to access this resource."

    def __init__(self, roles: list[RbacRoleEnum]) -> None:
        super().__init__()
        self.roles = roles

    async def has_permission(
        self,
        _source: Any,
        info: strawberry.Info[Context, Any],
        **_kwargs: Any,
    ) -> bool:
        for role in self.roles:
            if role in info.context.auth_info.roles:
                return True
        return False

    @override
    def on_unauthorized(self) -> None:
        raise self.error_class(
            message=f"You do not have permission to access this resource with role {', '.join(role.name.title() for role in self.roles)} role is required.",
            extensions={"statusCode": 403, "type": "RolePermissionError"},
        )
