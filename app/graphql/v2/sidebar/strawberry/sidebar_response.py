import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import RbacRoleEnum
from commons.db.v6.core import (
    RoleSidebarAssignment,
    SidebarConfiguration,
    SidebarGroupId,
)

from app.graphql.v2.sidebar.services import (
    EffectiveGroup,
    EffectiveItem,
    EffectiveSidebar,
)


@strawberry.type
class SidebarItemResponse:
    item_id: str
    order: int
    enabled: bool


@strawberry.type
class SidebarGroupResponse:
    group_id: SidebarGroupId
    order: int
    collapsed: bool
    items: list[SidebarItemResponse]


@strawberry.type
class SidebarConfigurationResponse:
    id: UUID
    name: str
    owner_type: str
    is_default: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    groups: list[SidebarGroupResponse]

    @classmethod
    def from_model(cls, model: SidebarConfiguration) -> Self:
        # Build group responses
        group_map: dict[SidebarGroupId, tuple[int, bool]] = {}
        for group in model.groups:
            group_map[group.group_id] = (group.group_order, group.collapsed)

        # Build items by group
        items_by_group: dict[SidebarGroupId, list[SidebarItemResponse]] = {}
        for item in model.items:
            if item.group_id not in items_by_group:
                items_by_group[item.group_id] = []
            items_by_group[item.group_id].append(
                SidebarItemResponse(
                    item_id=item.item_id,
                    order=item.item_order,
                    enabled=item.enabled,
                )
            )

        # Sort items within groups
        for items in items_by_group.values():
            items.sort(key=lambda x: x.order)

        # Build group responses
        groups: list[SidebarGroupResponse] = []
        for group_id, (order, collapsed) in sorted(
            group_map.items(), key=lambda x: x[1][0]
        ):
            groups.append(
                SidebarGroupResponse(
                    group_id=group_id,
                    order=order,
                    collapsed=collapsed,
                    items=items_by_group.get(group_id, []),
                )
            )

        return cls(
            id=model.id,
            name=model.name,
            owner_type=model.owner_type.name.lower(),
            is_default=model.is_default,
            created_at=model.created_at,
            updated_at=model.updated_at,
            groups=groups,
        )


@strawberry.type
class RoleSidebarAssignmentResponse:
    role: RbacRoleEnum
    configuration: SidebarConfigurationResponse
    assigned_at: datetime.datetime

    @classmethod
    def from_model(cls, model: RoleSidebarAssignment) -> Self:
        return cls(
            role=model.role,
            configuration=SidebarConfigurationResponse.from_model(model.configuration),
            assigned_at=model.assigned_at,
        )


@strawberry.type
class EffectiveSidebarItemResponse:
    item_id: str
    order: int
    enabled: bool
    is_configurable: bool

    @classmethod
    def from_dataclass(cls, item: EffectiveItem) -> Self:
        return cls(
            item_id=item.item_id,
            order=item.order,
            enabled=item.enabled,
            is_configurable=item.is_configurable,
        )


@strawberry.type
class EffectiveSidebarGroupResponse:
    group_id: SidebarGroupId
    order: int
    collapsed: bool
    items: list[EffectiveSidebarItemResponse]

    @classmethod
    def from_dataclass(cls, group: EffectiveGroup) -> Self:
        return cls(
            group_id=group.group_id,
            order=group.order,
            collapsed=group.collapsed,
            items=[EffectiveSidebarItemResponse.from_dataclass(i) for i in group.items],
        )


@strawberry.type
class EffectiveSidebarResponse:
    groups: list[EffectiveSidebarGroupResponse]
    source_type: str
    source_name: str | None

    @classmethod
    def from_dataclass(cls, sidebar: EffectiveSidebar) -> Self:
        return cls(
            groups=[
                EffectiveSidebarGroupResponse.from_dataclass(g) for g in sidebar.groups
            ],
            source_type=sidebar.source_type,
            source_name=sidebar.source_name,
        )


@strawberry.type
class ConfigurableSidebarItemResponse:
    item_id: str
    is_configurable: bool


@strawberry.type
class ConfigurableSidebarResponse:
    admin_hidden_items: list[str]
