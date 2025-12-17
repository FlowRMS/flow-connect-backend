from collections import defaultdict

from commons.auth import AuthInfo

from app.graphql.v2.rbac.models.enums import (
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
    RbacRoleEnum,
)
from app.graphql.v2.rbac.repositories.rbac_repository import RbacRepository
from app.graphql.v2.rbac.strawberry.rbac_grid_response import (
    RbacGridResponse,
    RbacPrivilegeResponse,
    RbacRolePermissionResponse,
)


class RbacService:
    def __init__(
        self,
        repository: RbacRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def get_rbac_grid(self) -> list[RbacGridResponse]:
        permissions = await self.repository.get_all_permissions()

        resource_map: dict[int, dict[int, list[RbacPrivilegeResponse]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for permission in permissions:
            if permission.resource and permission.role and permission.privilege:
                resource_map[int(permission.resource)][int(permission.role)].append(
                    RbacPrivilegeResponse(
                        privilege=RbacPrivilegeTypeEnum(int(permission.privilege)),
                        option=RbacPrivilegeOptionEnum(int(permission.option)),
                    )
                )

        result = []
        for resource_int, roles_dict in sorted(resource_map.items()):
            roles = []
            for role_int, privileges in sorted(roles_dict.items()):
                role_enum = RbacRoleEnum.from_int(role_int)
                roles.append(
                    RbacRolePermissionResponse(
                        role_name=role_enum.label if role_enum else f"Role {role_int}",
                        privileges=privileges,
                    )
                )

            result.append(
                RbacGridResponse(
                    resource=RbacResourceEnum(resource_int),
                    roles=roles,
                )
            )

        return result