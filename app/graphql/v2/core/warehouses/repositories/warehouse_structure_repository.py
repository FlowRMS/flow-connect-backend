from uuid import UUID

from commons.db.v6 import WarehouseStructure
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class WarehouseStructureRepository(BaseRepository[WarehouseStructure]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseStructure,
        )

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseStructure]:
        stmt = (
            select(WarehouseStructure)
            .where(WarehouseStructure.warehouse_id == warehouse_id)
            .order_by(WarehouseStructure.level_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_warehouse(self, warehouse_id: UUID) -> None:
        stmt = select(WarehouseStructure).where(
            WarehouseStructure.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        for item in result.scalars().all():
            await self.session.delete(item)
        await self.session.flush()
