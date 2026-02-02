import uuid
from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.jobs.jobs_model import Job

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class JobInput(BaseInputGQL[Job]):
    job_name: str
    status_id: uuid.UUID
    start_date: date | None = strawberry.UNSET
    end_date: date | None = strawberry.UNSET
    job_owner_id: UUID | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    job_type: str | None = strawberry.UNSET
    structural_details: str | None = strawberry.UNSET
    structural_information: str | None = strawberry.UNSET
    additional_information: str | None = strawberry.UNSET
    requester_id: UUID | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET

    def to_orm_model(self) -> Job:
        return Job(
            job_name=self.job_name,
            start_date=self.optional_field(self.start_date),  # pyright: ignore[reportArgumentType]
            end_date=self.optional_field(self.end_date),  # pyright: ignore[reportArgumentType]
            status_id=self.status_id,
            job_owner_id=self.optional_field(self.job_owner_id),
            description=self.optional_field(self.description),
            job_type=self.optional_field(self.job_type),
            structural_details=self.optional_field(self.structural_details),
            structural_information=self.optional_field(self.structural_information),
            additional_information=self.optional_field(self.additional_information),
            requester_id=self.optional_field(self.requester_id),
            tags=self.optional_field(self.tags),
        )
