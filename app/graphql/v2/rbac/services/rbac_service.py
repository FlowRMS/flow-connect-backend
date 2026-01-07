from collections import defaultdict

from commons.auth import AuthInfo
from commons.db.v6 import (
    RbacPermission,
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
    RbacRoleEnum,
    RbacRoleSetting,
)

from app.graphql.v2.rbac.repositories.rbac_repository import RbacRepository
from app.graphql.v2.rbac.strawberry.rbac_grid_input import RbacGridInput
from app.graphql.v2.rbac.strawberry.rbac_grid_response import (
    RbacGridResponse,
    RbacPrivilegeResponse,
    RbacRolePermissionResponse,
)
from app.graphql.v2.rbac.strawberry.user_rbac_response import Privilege, UserRbac


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

        resource_map: dict[
            RbacResourceEnum, dict[RbacRoleEnum, list[RbacPrivilegeResponse]]
        ] = defaultdict(lambda: defaultdict(list))

        for permission in permissions:
            if permission.resource and permission.role and permission.privilege:
                resource_map[permission.resource][permission.role].append(
                    RbacPrivilegeResponse(
                        privilege=permission.privilege,
                        option=permission.option,
                    )
                )

        result = []
        for resource_int, roles_dict in sorted(resource_map.items()):
            roles = []
            for role_enum, privileges in sorted(roles_dict.items()):
                roles.append(
                    RbacRolePermissionResponse(
                        role_name=role_enum,
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
        self, grid_inputs: list[RbacGridInput]
    ) -> list[RbacGridResponse]:
        permissions_to_create = []
        for grid_input in grid_inputs:
            resource = grid_input.resource
            if resource.is_immutable():
                continue

            for role_input in grid_input.roles:
                await self.repository.delete_by_role_and_resource(
                    role_input.role, resource
                )

                for privilege_input in role_input.privileges:
                    permission = RbacPermission(
                        resource=resource,
                        role=role_input.role,
                        privilege=privilege_input.privilege,
                        option=privilege_input.option,
                    )
                    permissions_to_create.append(permission)

        if permissions_to_create:
            _ = await self.repository.create_permissions(permissions_to_create)

        return await self.get_rbac_grid()

    async def get_user_rbac(self, resource: RbacResourceEnum) -> UserRbac:
        permissions = await self.repository.get_permissions_by_resource_and_roles(
            resource, self.auth_info.roles
        )

        privilege_map: dict[RbacPrivilegeTypeEnum, RbacPrivilegeOptionEnum] = {}
        for permission in permissions:
            privilege = permission.privilege
            option = permission.option
            if privilege in privilege_map:
                if option > privilege_map[privilege]:
                    privilege_map[privilege] = option
            else:
                privilege_map[privilege] = option

        privileges = [
            Privilege(privilege=privilege, option=option)
            for privilege, option in sorted(privilege_map.items())
        ]

        role_setting = await self.repository.get_role_settings_by_roles(
            self.auth_info.roles[0]
        )
        return UserRbac(privileges=privileges, commission=role_setting.commission)

    async def update_commission_visibility(
        self,
        role: RbacRoleEnum,
        commission: bool,
    ) -> RbacRoleSetting:
        return await self.repository.update_role_setting_commission(role, commission)

    async def get_all_role_settings(self) -> list[RbacRoleSetting]:
        return await self.repository.get_all_role_settings()
