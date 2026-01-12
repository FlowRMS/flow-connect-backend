from uuid import UUID

from commons.db.v6 import RbacRoleEnum
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.v2.sidebar.models import (
    RoleSidebarAssignment,
    SidebarConfiguration,
    UserActiveSidebar,
)


class RoleSidebarRepository:
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__()
        self.session = session
        self.context = context_wrapper.get()

    async def get_role_assignment(
        self, role: RbacRoleEnum
    ) -> RoleSidebarAssignment | None:
        stmt = (
            select(RoleSidebarAssignment)
            .where(RoleSidebarAssignment.role == role)
            .options(
                selectinload(RoleSidebarAssignment.configuration).selectinload(
                    SidebarConfiguration.groups
                ),
                selectinload(RoleSidebarAssignment.configuration).selectinload(
                    SidebarConfiguration.items
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all_role_assignments(self) -> list[RoleSidebarAssignment]:
        stmt = (
            select(RoleSidebarAssignment)
            .options(
                selectinload(RoleSidebarAssignment.configuration).selectinload(
                    SidebarConfiguration.groups
                ),
                selectinload(RoleSidebarAssignment.configuration).selectinload(
                    SidebarConfiguration.items
                ),
            )
            .order_by(RoleSidebarAssignment.role)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def assign_to_role(
        self,
        role: RbacRoleEnum,
        configuration_id: UUID,
        assigned_by_id: UUID,
    ) -> RoleSidebarAssignment:
        # Delete existing assignment if any
        _ = await self.session.execute(
            delete(RoleSidebarAssignment).where(RoleSidebarAssignment.role == role)
        )

        assignment = RoleSidebarAssignment(
            role=role,
            configuration_id=configuration_id,
            assigned_by_id=assigned_by_id,
        )
        self.session.add(assignment)
        await self.session.flush()
        return await self.get_role_assignment(role)  # type: ignore

    async def remove_role_assignment(self, role: RbacRoleEnum) -> bool:
        stmt = delete(RoleSidebarAssignment).where(RoleSidebarAssignment.role == role)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0  # type: ignore[union-attr]

    async def get_user_active_sidebar(self, user_id: UUID) -> UserActiveSidebar | None:
        stmt = (
            select(UserActiveSidebar)
            .where(UserActiveSidebar.user_id == user_id)
            .options(
                selectinload(UserActiveSidebar.configuration).selectinload(
                    SidebarConfiguration.groups
                ),
                selectinload(UserActiveSidebar.configuration).selectinload(
                    SidebarConfiguration.items
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def set_user_active_sidebar(
        self,
        user_id: UUID,
        configuration_id: UUID | None,
    ) -> UserActiveSidebar:
        existing = await self.get_user_active_sidebar(user_id)
        if existing:
            existing.configuration_id = configuration_id
            await self.session.flush()
            return existing

        active = UserActiveSidebar(
            user_id=user_id,
            configuration_id=configuration_id,
        )
        self.session.add(active)
        await self.session.flush()
        return active
