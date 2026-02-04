from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.tasks.task_assignee_model import TaskAssignee
from commons.db.v6.crm.tasks.task_model import Task
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.tasks.processors import SyncTaskAssigneesProcessor
from app.graphql.tasks.repositories.task_landing_query_builder import (
    TaskLandingQueryBuilder,
)
from app.graphql.tasks.strawberry.task_landing_page_response import (
    TaskLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy
from app.graphql.v2.rbac.strategies.sales_team_filter import SalesTeamFilterStrategy


class TasksRepository(BaseRepository[Task]):
    landing_model = TaskLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.TASK

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        sync_assignees_processor: SyncTaskAssigneesProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Task,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[sync_assignees_processor],
        )
        self.sync_assignees_processor = sync_assignees_processor

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        if RbacRoleEnum.SALES_MANAGER in self.auth_info.roles:
            return SalesTeamFilterStrategy(
                RbacResourceEnum.TASK,
                Task.created_by_id,
            )
        return CreatedByFilterStrategy(
            RbacResourceEnum.TASK,
            Task,
        )

    def paginated_stmt(self) -> Select[Any]:
        return TaskLandingQueryBuilder().build()

    async def search_by_title(self, search_term: str, limit: int = 20) -> list[Task]:
        """
        Search tasks by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against task title
            limit: Maximum number of tasks to return (default: 20)

        Returns:
            List of Task objects matching the search criteria
        """
        stmt = (
            select(Task)
            .options(
                joinedload(Task.created_by),
                joinedload(Task.category),
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            )
            .where(Task.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Task]:
        stmt = (
            select(Task)
            .options(
                joinedload(Task.created_by),
                joinedload(Task.category),
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            )
            .join(
                LinkRelation,
                or_(
                    # Tasks as source, entity as target
                    (
                        (LinkRelation.source_entity_type == EntityType.TASK)
                        & (LinkRelation.target_entity_type == entity_type)
                        & (LinkRelation.target_entity_id == entity_id)
                        & (LinkRelation.source_entity_id == Task.id)
                    ),
                    # Entity as source, Tasks as target
                    (
                        (LinkRelation.source_entity_type == entity_type)
                        & (LinkRelation.target_entity_type == EntityType.TASK)
                        & (LinkRelation.source_entity_id == entity_id)
                        & (LinkRelation.target_entity_id == Task.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
