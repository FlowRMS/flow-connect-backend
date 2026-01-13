from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.tasks.services.tasks_service import TasksService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class TaskWatcherMutations:
    @strawberry.mutation
    @inject
    async def add_task_watcher(
        self,
        task_id: UUID,
        user_id: UUID,
        tasks_service: Injected[TasksService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await tasks_service.find_task_by_id(task_id)
        users = await watcher_service.add_watcher(EntityType.TASK, task_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]

    @strawberry.mutation
    @inject
    async def remove_task_watcher(
        self,
        task_id: UUID,
        user_id: UUID,
        tasks_service: Injected[TasksService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await tasks_service.find_task_by_id(task_id)
        users = await watcher_service.remove_watcher(EntityType.TASK, task_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]
