from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class JobWatcherMutations:
    @strawberry.mutation
    @inject
    async def add_job_watcher(
        self,
        job_id: UUID,
        user_id: UUID,
        jobs_service: Injected[JobsService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await jobs_service.get_job(job_id)
        users = await watcher_service.add_watcher(EntityType.JOB, job_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]

    @strawberry.mutation
    @inject
    async def remove_job_watcher(
        self,
        job_id: UUID,
        user_id: UUID,
        jobs_service: Injected[JobsService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await jobs_service.get_job(job_id)
        users = await watcher_service.remove_watcher(EntityType.JOB, job_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]
