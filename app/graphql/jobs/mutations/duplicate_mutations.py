import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.confirmed_different_service import (
    ConfirmedDifferentService,
)
from app.graphql.jobs.services.job_merge_service import FieldSelection, JobMergeService
from app.graphql.jobs.strawberry.duplicate_input import (
    ConfirmDifferentInput,
    MergeJobsInput,
)
from app.graphql.jobs.strawberry.duplicate_response import MergeResultType


@strawberry.type
class DuplicateDetectionMutations:
    @strawberry.mutation
    @inject
    async def merge_jobs(
        self,
        input: MergeJobsInput,
        merge_service: Injected[JobMergeService],
    ) -> MergeResultType:
        field_selections = None
        if input.field_selections is not strawberry.UNSET and input.field_selections:
            field_selections = [
                FieldSelection(
                    field_name=fs.field_name,
                    source_job_id=fs.source_job_id,
                )
                for fs in input.field_selections
            ]

        result = await merge_service.merge_jobs(
            primary_job_id=input.primary_job_id,
            duplicate_job_ids=input.duplicate_job_ids,
            field_selections=field_selections,
        )
        return MergeResultType.from_result(result)

    @strawberry.mutation
    @inject
    async def confirm_jobs_different(
        self,
        input: ConfirmDifferentInput,
        confirmed_service: Injected[ConfirmedDifferentService],
    ) -> bool:
        reason = None
        if input.reason is not strawberry.UNSET:
            reason = input.reason

        _ = await confirmed_service.confirm_jobs_different(
            source_job_id=input.source_job_id,
            target_job_id=input.target_job_id,
            reason=reason,
        )
        return True
