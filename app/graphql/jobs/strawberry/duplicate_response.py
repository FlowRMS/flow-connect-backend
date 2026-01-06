from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from app.graphql.jobs.services.job_duplicate_detection_service import (
    DuplicateJobGroup,
    DuplicateScanResult,
    SimilarJobResult,
)
from app.graphql.jobs.services.job_merge_service import MergeResult
from app.graphql.jobs.strawberry.job_response import JobLiteType, JobType


@strawberry.type
class SimilarJobType:
    job: JobLiteType
    confidence: Decimal
    match_reasons: list[str]

    @classmethod
    def from_result(cls, result: SimilarJobResult) -> Self:
        return cls(
            job=JobLiteType.from_orm_model(result.job),
            confidence=result.confidence,
            match_reasons=result.match_reasons,
        )


@strawberry.type
class DuplicateJobGroupType:
    id: UUID
    jobs: list[JobLiteType]
    confidence: Decimal
    match_reasons: list[str]

    @classmethod
    def from_group(cls, group: DuplicateJobGroup) -> Self:
        return cls(
            id=group.id,
            jobs=[JobLiteType.from_orm_model(j) for j in group.jobs],
            confidence=group.confidence,
            match_reasons=group.match_reasons,
        )


@strawberry.type
class DuplicateScanResultType:
    groups: list[DuplicateJobGroupType]
    total_jobs_scanned: int

    @classmethod
    def from_result(cls, result: DuplicateScanResult) -> Self:
        return cls(
            groups=[DuplicateJobGroupType.from_group(g) for g in result.groups],
            total_jobs_scanned=result.total_jobs_scanned,
        )


@strawberry.type
class MergeResultType:
    merged_job: JobType
    jobs_deleted_count: int
    entities_transferred_count: int

    @classmethod
    def from_result(cls, result: MergeResult) -> Self:
        return cls(
            merged_job=JobType.from_orm_model(result.merged_job),
            jobs_deleted_count=result.jobs_deleted_count,
            entities_transferred_count=result.entities_transferred_count,
        )
