from uuid import UUID

from commons.db.v6 import WarehouseMember
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class WarehouseMembersRepository(BaseRepository[WarehouseMember]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseMember,
        )

    async def get_by_warehouse_and_user(
        self,
        warehouse_id: UUID,
        user_id: UUID,
    ) -> WarehouseMember | None:
        stmt = select(WarehouseMember).where(
            WarehouseMember.warehouse_id == warehouse_id,
            WarehouseMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseMember]:
        stmt = select(WarehouseMember).where(
            WarehouseMember.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
