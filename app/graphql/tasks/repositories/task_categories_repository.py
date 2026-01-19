from commons.db.v6.crm.tasks import TaskCategory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class TaskCategoriesRepository(BaseRepository[TaskCategory]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, TaskCategory)

    async def list_active(self) -> list[TaskCategory]:
        stmt = (
            select(TaskCategory)
            .where(TaskCategory.is_active.is_(True))
            .order_by(TaskCategory.display_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_ordered(self) -> list[TaskCategory]:
        stmt = select(TaskCategory).order_by(TaskCategory.display_order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> TaskCategory | None:
        stmt = select(TaskCategory).where(TaskCategory.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
