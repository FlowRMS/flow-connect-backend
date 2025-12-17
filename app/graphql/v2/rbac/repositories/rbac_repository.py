from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.rbac.models.rbac_permission import RbacPermission


class RbacRepository(BaseRepository[RbacPermission]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, RbacPermission)

    async def get_all_permissions(self) -> list[RbacPermission]:
        stmt = select(RbacPermission).order_by(
            RbacPermission.resource, RbacPermission.role, RbacPermission.privilege
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())