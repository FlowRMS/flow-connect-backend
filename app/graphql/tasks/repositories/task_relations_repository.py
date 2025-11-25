from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.tasks.models.task_relation_model import TaskRelation


class TaskRelationsRepository(BaseRepository[TaskRelation]):
    """Repository for TaskRelations entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, TaskRelation)
