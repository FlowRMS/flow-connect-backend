from uuid import UUID

from commons.db.v6 import Warehouse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Warehouse,
        )

    async def get_with_relations(self, warehouse_id: UUID) -> Warehouse | None:
        stmt = (
            select(Warehouse)
            .options(
                selectinload(Warehouse.members),
                selectinload(Warehouse.settings),
                selectinload(Warehouse.structure),
            )
            .where(Warehouse.id == warehouse_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all_with_relations(self) -> list[Warehouse]:
        stmt = select(Warehouse).options(
            selectinload(Warehouse.members),
            selectinload(Warehouse.settings),
            selectinload(Warehouse.structure),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
