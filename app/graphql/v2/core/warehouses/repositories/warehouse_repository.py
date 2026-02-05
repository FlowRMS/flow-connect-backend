from uuid import UUID

from commons.db.v6 import Warehouse
from sqlalchemy import Select, select
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

    @property
    def base_query(self) -> Select[tuple[Warehouse]]:
        """Base query with standard eager loading for warehouses."""
        return select(Warehouse).options(
            selectinload(Warehouse.members),
            selectinload(Warehouse.settings),
            selectinload(Warehouse.structure),
        )

    async def get_with_relations(self, warehouse_id: UUID) -> Warehouse | None:
        stmt = self.base_query.where(
            Warehouse.id == warehouse_id,
            Warehouse.is_active != False,  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all_with_relations(self) -> list[Warehouse]:
        stmt = self.base_query.where(Warehouse.is_active != False)  # noqa: E712
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def soft_delete(self, warehouse_id: UUID) -> Warehouse | None:
        """Soft-delete a warehouse by setting is_active = False."""
        stmt = select(Warehouse).where(Warehouse.id == warehouse_id)
        result = await self.session.execute(stmt)
        warehouse = result.scalar_one_or_none()
        if not warehouse:
            return None
        warehouse.is_active = False
        await self.session.flush()
        return warehouse
