from collections import defaultdict

from commons.auth import AuthInfo

from app.graphql.v2.rbac.models.entities.rbac_permission import RbacPermission
from app.graphql.v2.rbac.models.enums.rbac_privilege_option_enum import RbacPrivilegeOptionEnum
from app.graphql.v2.rbac.models.enums.rbac_privilege_type_enum import RbacPrivilegeTypeEnum
from app.graphql.v2.rbac.models.enums.rbac_resource_enum import RbacResourceEnum
from app.graphql.v2.rbac.models.enums.rbac_role_enum import RbacRoleEnum
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
        super().__init__()
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

    async def update_rbac_grid(
        self, grid_inputs: list
    ) -> list[RbacGridResponse]:
        permissions_to_create = []
        for grid_input in grid_inputs:
            resource = grid_input.resource
            if resource.immutable:
                continue

            for role_input in grid_input.roles:
                role_enum = RbacRoleEnum.from_label(role_input.role_name)

                if not role_enum or role_enum.immutable:
                    continue

                # Delete existing permissions for this role and resource
                await self.repository.delete_by_role_and_resource(role_enum, resource)

                for privilege_input in role_input.privileges:
                    permission = RbacPermission(
                        resource=resource,
                        role=role_enum.num,
                        privilege=privilege_input.privilege,
                        option=privilege_input.option,
                    )
                    permissions_to_create.append(permission)

        if permissions_to_create:
            _ = await self.repository.create_permissions(permissions_to_create)

        return await self.get_rbac_grid()
