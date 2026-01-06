from typing import Annotated, Any, override

import strawberry
from aioinject import Inject
from aioinject.ext.strawberry import inject
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from strawberry import BasePermission

from app.core.context_wrapper import ContextWrapper


class RolePermissionAccess(BasePermission):
    role: RbacRoleEnum = RbacRoleEnum.ADMINISTRATOR
    message = "You do not have permission to access this resource."

    def __init__(self, role: RbacRoleEnum) -> None:
        super().__init__()
        self.role = role

    @inject
    async def has_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        source: Any,
        info: strawberry.Info,
        context_wrapper: Annotated[ContextWrapper, Inject],
        **kwargs: Any,
    ) -> bool:
        context = context_wrapper.get()
        return self.role in context.auth_info.roles

    @override
    def on_unauthorized(self) -> None:
        raise self.error_class(
            message=f"You do not have permission to access this resource with role {self.role.name.title()} role is required.",
            extensions={"statusCode": 403, "type": "RolePermissionError"},
        )
