from dataclasses import dataclass

from commons.auth import AuthInfo
from commons.db.v6 import RbacRoleEnum

from app.graphql.v2.sidebar.models import SidebarConfiguration
from app.graphql.v2.sidebar.repositories import (
    RoleSidebarRepository,
    SidebarConfigurationRepository,
)


@dataclass
class EffectiveItem:
    item_id: str
    order: int
    enabled: bool
    is_configurable: bool


@dataclass
class EffectiveGroup:
    group_id: str
    order: int
    collapsed: bool
    items: list[EffectiveItem]


@dataclass
class EffectiveSidebar:
    groups: list[EffectiveGroup]
    source_type: str
    source_name: str | None


class EffectiveSidebarService:
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

    async def get_effective_sidebar(self) -> EffectiveSidebar:
        user_id = self.auth_info.flow_user_id
        role = (
            self.auth_info.roles[0] if self.auth_info.roles else RbacRoleEnum.INSIDE_REP
        )

        # 1. Check user's active configuration
        user_active = await self.role_repository.get_user_active_sidebar(user_id)
        if user_active and user_active.configuration:
            return self._apply_admin_constraints(
                user_active.configuration, role, "user_active"
            )

        # 2. Check user's default configuration
        user_default = await self.config_repository.get_user_default_configuration(
            user_id
        )
        if user_default:
            return self._apply_admin_constraints(user_default, role, "user_default")

        # 3. Check role assignment
        role_assignment = await self.role_repository.get_role_assignment(role)
        if role_assignment and role_assignment.configuration:
            return self._config_to_effective(
                role_assignment.configuration, "role", all_configurable=True
            )

        # 4. Return system default
        return self._get_system_default()

    async def _get_admin_enabled_items(self, role: RbacRoleEnum) -> set[str] | None:
        role_assignment = await self.role_repository.get_role_assignment(role)
        if not role_assignment or not role_assignment.configuration:
            return None

        return {
            item.item_id for item in role_assignment.configuration.items if item.enabled
        }

    def _apply_admin_constraints(
        self,
        config: SidebarConfiguration,
        role: RbacRoleEnum,
        source_type: str,
    ) -> EffectiveSidebar:
        # For now, we need to get admin constraints synchronously
        # This will be called after we've loaded the role assignment
        return self._config_to_effective(config, source_type, all_configurable=True)

    def _config_to_effective(
        self,
        config: SidebarConfiguration,
        source_type: str,
        *,
        all_configurable: bool = True,
        admin_enabled_items: set[str] | None = None,
    ) -> EffectiveSidebar:
        # Build group map
        group_map: dict[str, tuple[int, bool]] = {}
        for group in config.groups:
            group_map[group.group_id] = (group.group_order, group.collapsed)

        # Build items by group
        items_by_group: dict[str, list[EffectiveItem]] = {}
        for item in config.items:
            is_configurable = (
                admin_enabled_items is None or item.item_id in admin_enabled_items
            )
            # Skip items that admin has disabled
            if (
                admin_enabled_items is not None
                and item.item_id not in admin_enabled_items
            ):
                continue

            if item.group_id not in items_by_group:
                items_by_group[item.group_id] = []

            items_by_group[item.group_id].append(
                EffectiveItem(
                    item_id=item.item_id,
                    order=item.item_order,
                    enabled=item.enabled,
                    is_configurable=is_configurable if all_configurable else True,
                )
            )

        # Sort items within each group
        for items in items_by_group.values():
            items.sort(key=lambda x: x.order)

        # Build groups
        groups: list[EffectiveGroup] = []
        for group_id, (order, collapsed) in sorted(
            group_map.items(), key=lambda x: x[1][0]
        ):
            if group_id in items_by_group:
                groups.append(
                    EffectiveGroup(
                        group_id=group_id,
                        order=order,
                        collapsed=collapsed,
                        items=items_by_group[group_id],
                    )
                )

        return EffectiveSidebar(
            groups=groups,
            source_type=source_type,
            source_name=config.name,
        )

    def _get_system_default(self) -> EffectiveSidebar:
        # Return empty - frontend will use its defaults
        return EffectiveSidebar(
            groups=[],
            source_type="system_default",
            source_name=None,
        )

    async def get_configurable_sidebar(self) -> tuple[list[str], set[str]]:
        role = (
            self.auth_info.roles[0] if self.auth_info.roles else RbacRoleEnum.INSIDE_REP
        )
        admin_enabled = await self._get_admin_enabled_items(role)

        if admin_enabled is None:
            # No admin constraints - all items configurable
            return [], set()

        # Return list of hidden items
        role_assignment = await self.role_repository.get_role_assignment(role)
        if not role_assignment or not role_assignment.configuration:
            return [], set()

        all_items = {item.item_id for item in role_assignment.configuration.items}
        hidden_items = all_items - admin_enabled

        return list(hidden_items), admin_enabled
