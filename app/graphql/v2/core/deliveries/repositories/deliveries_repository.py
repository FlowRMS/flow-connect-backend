from uuid import UUID

from commons.db.v6 import Delivery
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class DeliveriesRepository(BaseRepository[Delivery]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, Delivery)

    def _with_relations(self, stmt: Select[Delivery]) -> Select[Delivery]:
        return stmt.options(
            selectinload(Delivery.items),
            selectinload(Delivery.status_history),
            selectinload(Delivery.issues),
            selectinload(Delivery.assignees),
            selectinload(Delivery.documents),
            selectinload(Delivery.recurring_shipment),
        )

    async def get_with_relations(self, delivery_id: UUID) -> Delivery | None:
        stmt = self._with_relations(
            select(Delivery).where(Delivery.id == delivery_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[Delivery]:
        stmt = self._with_relations(
            select(Delivery).where(Delivery.warehouse_id == warehouse_id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def list_all_with_relations(self) -> list[Delivery]:
        stmt = self._with_relations(select(Delivery))
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
