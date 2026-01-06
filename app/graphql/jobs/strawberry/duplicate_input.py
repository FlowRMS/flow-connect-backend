from uuid import UUID

import strawberry


@strawberry.input
class ScanDuplicatesInput:
    job_id: UUID | None = strawberry.UNSET
    status_filter: list[str] | None = strawberry.UNSET
    days_back: int | None = strawberry.UNSET


@strawberry.input
class FieldSelectionInput:
    field_name: str
    source_job_id: UUID


@strawberry.input
class MergeJobsInput:
    primary_job_id: UUID
    duplicate_job_ids: list[UUID]
    field_selections: list[FieldSelectionInput] | None = strawberry.UNSET


@strawberry.input
class ConfirmDifferentInput:
    job_id_1: UUID
    job_id_2: UUID
    reason: str | None = strawberry.UNSET
