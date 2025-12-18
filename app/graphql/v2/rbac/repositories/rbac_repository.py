from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.rbac.models.entities.rbac_permission import RbacPermission
from app.graphql.v2.rbac.models.enums.rbac_resource_enum import RbacResourceEnum
from app.graphql.v2.rbac.models.enums.rbac_role_enum import RbacRoleEnum


class RbacRepository(BaseRepository[RbacPermission]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, RbacPermission)

    async def get_all_permissions(self) -> list[RbacPermission]:
        stmt = select(RbacPermission).order_by(
            RbacPermission.resource, RbacPermission.role, RbacPermission.privilege
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_role_and_resource(self, role: RbacRoleEnum, resource: RbacResourceEnum) -> None:
        stmt = delete(RbacPermission).where(
            RbacPermission.role == role,
            RbacPermission.resource == resource
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def create_permissions(
        self, permissions: list[RbacPermission]
    ) -> list[RbacPermission]:
        for permission in permissions:
            self.session.add(permission)
        await self.session.flush()
        return permissions
