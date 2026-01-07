from uuid import UUID

from commons.db.v6 import WarehouseSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class WarehouseSettingsRepository(BaseRepository[WarehouseSettings]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseSettings,
        )

    async def get_by_warehouse(self, warehouse_id: UUID) -> WarehouseSettings | None:
        stmt = select(WarehouseSettings).where(
            WarehouseSettings.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
