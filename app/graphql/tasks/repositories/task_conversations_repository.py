"""Repository for TaskConversation entity."""

from uuid import UUID

from commons.db.v6.crm.tasks.task_conversation_model import TaskConversation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class TaskConversationsRepository(BaseRepository[TaskConversation]):
    """Repository for TaskConversations entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, TaskConversation)

    async def get_by_task_id(self, task_id: UUID) -> list[TaskConversation]:
        """Get all conversations for a specific task."""
        stmt = (
            select(TaskConversation)
            .options(joinedload(TaskConversation.created_by))
            .where(TaskConversation.task_id == task_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
