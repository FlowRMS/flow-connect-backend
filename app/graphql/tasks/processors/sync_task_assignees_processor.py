from uuid import UUID

from commons.db.v6.crm.tasks.task_assignee_model import TaskAssignee
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class SyncTaskAssigneesProcessor(BaseProcessor[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session
        self._pending_assignee_ids: dict[UUID, list[UUID]] = {}

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.POST_CREATE, RepositoryEvent.POST_UPDATE]

    def set_assignee_ids(self, task_id: UUID, assignee_ids: list[UUID]) -> None:
        self._pending_assignee_ids[task_id] = assignee_ids

    async def process(self, context: EntityContext[Task]) -> None:
        task_id = context.entity_id
        assignee_ids = self._pending_assignee_ids.pop(task_id, None)

        if assignee_ids is None:
            return

        task = context.entity
        if not hasattr(task, "assignees") or task.assignees is None:
            from sqlalchemy import select

            result = await self.session.execute(
                select(Task)
                .options(selectinload(Task.assignees))
                .where(Task.id == task_id)
            )
            task = result.scalar_one()

        await self._sync_assignees(task, assignee_ids)
        await self.session.flush()

    async def _sync_assignees(self, task: Task, assignee_ids: list[UUID]) -> None:
        current_ids = {ta.user_id for ta in task.assignees}
        new_ids = set(assignee_ids)

        for ta in list(task.assignees):
            if ta.user_id not in new_ids:
                task.assignees.remove(ta)

        for user_id in new_ids - current_ids:
            task.assignees.append(TaskAssignee(task_id=task.id, user_id=user_id))
