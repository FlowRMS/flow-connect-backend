from uuid import UUID

from commons.db.v6.crm.tasks.task_assignee_model import TaskAssignee
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.ext.asyncio import AsyncSession

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
        assignees = await task.awaitable_attrs.assignees

        current_ids = {ta.user_id for ta in assignees}
        new_ids = set(assignee_ids)

        for ta in list(assignees):
            if ta.user_id not in new_ids:
                assignees.remove(ta)

        for user_id in new_ids - current_ids:
            assignees.append(TaskAssignee(task_id=task.id, user_id=user_id))

        await self.session.flush()
