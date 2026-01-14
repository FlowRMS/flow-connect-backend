from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import RbacRoleEnum
from commons.db.v6.crm import (
    RoleSidebarAssignment,
    SidebarConfiguration,
    SidebarConfigurationGroup,
    SidebarConfigurationItem,
    SidebarOwnerType,
)

from app.graphql.v2.sidebar.repositories import (
    RoleSidebarRepository,
    SidebarConfigurationRepository,
)
from app.graphql.v2.sidebar.strawberry.sidebar_input import (
    SaveSidebarConfigurationInput,
)


class SidebarConfigurationService:
    def __init__(
        self,
        config_repository: SidebarConfigurationRepository,
        role_repository: RoleSidebarRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.config_repository = config_repository
        self.role_repository = role_repository
        self.auth_info = auth_info

    async def get_admin_configurations(self) -> list[SidebarConfiguration]:
        return await self.config_repository.get_admin_configurations()

    async def get_user_configurations(self) -> list[SidebarConfiguration]:
        return await self.config_repository.get_user_configurations(
            self.auth_info.flow_user_id
        )

    async def get_configuration_by_id(
        self, config_id: UUID
    ) -> SidebarConfiguration | None:
        return await self.config_repository.get_by_id(config_id)

    async def save_configuration(
        self,
        input: SaveSidebarConfigurationInput,
    ) -> SidebarConfiguration:
        user_id = self.auth_info.flow_user_id

        # Determine owner based on config type
        owner_type = (
            SidebarOwnerType.ADMIN if input.is_admin_config else SidebarOwnerType.USER
        )
        owner_id = None if input.is_admin_config else user_id

        # Build groups and items from input
        groups = [
            SidebarConfigurationGroup(
                group_id=g.group_id,
                group_order=g.order,
                collapsed=g.collapsed,
            )
            for g in input.groups
        ]

        items = [
            SidebarConfigurationItem(
                group_id=g.group_id,
                item_id=item.item_id,
                item_order=item.order,
                enabled=item.enabled,
            )
            for g in input.groups
            for item in g.items
        ]

        if input.id:
            # Update existing
            config = await self.config_repository.get_by_id(
                input.id, load_relations=False
            )
            if not config:
                raise ValueError(f"Configuration {input.id} not found")

            config.name = input.name
            if input.is_default and not input.is_admin_config:
                await self.config_repository.clear_user_default(user_id)
                config.is_default = True

            return await self.config_repository.update(config, groups, items)
        else:
            # Create new
            is_default = bool(input.is_default) if not input.is_admin_config else False
            if is_default:
                await self.config_repository.clear_user_default(user_id)

            config = SidebarConfiguration(
                name=input.name,
                owner_type=owner_type,
                owner_id=owner_id,
                is_default=is_default,
                created_by_id=user_id,
            )
            return await self.config_repository.create(config, groups, items)

    async def delete_configuration(self, config_id: UUID) -> bool:
        return await self.config_repository.delete(config_id)

    async def get_role_assignments(self) -> list[RoleSidebarAssignment]:
        return await self.role_repository.get_all_role_assignments()

    async def assign_to_role(
        self,
        role: RbacRoleEnum,
        configuration_id: UUID,
    ) -> RoleSidebarAssignment:
        return await self.role_repository.assign_to_role(
            role=role,
            configuration_id=configuration_id,
            assigned_by_id=self.auth_info.flow_user_id,
        )

    async def remove_role_assignment(self, role: RbacRoleEnum) -> bool:
        return await self.role_repository.remove_role_assignment(role)

    async def set_active_configuration(self, configuration_id: UUID | None) -> bool:
        _ = await self.role_repository.set_user_active_sidebar(
            user_id=self.auth_info.flow_user_id,
            configuration_id=configuration_id,
        )
        return True
