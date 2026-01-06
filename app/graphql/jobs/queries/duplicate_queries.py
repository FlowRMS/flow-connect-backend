from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.job_duplicate_detection_service import (
    JobDuplicateDetectionService,
)
from app.graphql.jobs.services.jobs_service import JobsService
from app.graphql.jobs.strawberry.duplicate_input import ScanDuplicatesInput
from app.graphql.jobs.strawberry.duplicate_response import (
    DuplicateScanResultType,
    SimilarJobType,
)


@strawberry.type
class DuplicateDetectionQueries:
    @strawberry.field
    @inject
    async def scan_job_duplicates(
        self,
        detection_service: Injected[JobDuplicateDetectionService],
        input: ScanDuplicatesInput | None = None,
    ) -> DuplicateScanResultType:
        job_id = None
        status_filter = None
        days_back = None

        if input:
            if input.job_id is not strawberry.UNSET:
                job_id = input.job_id
            if input.status_filter is not strawberry.UNSET:
                status_filter = input.status_filter
            if input.days_back is not strawberry.UNSET:
                days_back = input.days_back

        result = await detection_service.scan_for_duplicates(
            job_id=job_id,
            status_filter=status_filter,
            days_back=days_back,
        )
        return DuplicateScanResultType.from_result(result)

    @strawberry.field
    @inject
    async def similar_jobs(
        self,
        job_id: UUID,
        jobs_service: Injected[JobsService],
        detection_service: Injected[JobDuplicateDetectionService],
        threshold: float = 0.70,
    ) -> list[SimilarJobType]:
        job = await jobs_service.get_job(job_id)
        results = await detection_service.find_similar_jobs(
            job=job,
            threshold=threshold,
        )
        return [SimilarJobType.from_result(r) for r in results]
