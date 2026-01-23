from uuid import UUID

import strawberry
from commons.db.v6 import RbacRoleEnum
from commons.db.v6.core import SidebarGroupId


@strawberry.input
class SidebarItemInput:
    item_id: str
    order: int
    enabled: bool


@strawberry.input
class SidebarGroupInput:
    group_id: SidebarGroupId
    order: int
    collapsed: bool
    items: list[SidebarItemInput]


@strawberry.input
class SaveSidebarConfigurationInput:
    name: str
    is_admin_config: bool
    groups: list[SidebarGroupInput]
    id: UUID | None = None
    is_default: bool | None = None


@strawberry.input
class AssignSidebarToRoleInput:
    role: RbacRoleEnum
    configuration_id: UUID
