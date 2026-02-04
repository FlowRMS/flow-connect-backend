import uuid
from typing import Self

import strawberry
from commons.db.v6.crm.jobs.job_status_model import JobStatus

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class JobStatusType(DTOMixin[JobStatus]):
    id: uuid.UUID
    name: str

    @classmethod
    def from_orm_model(cls, model: JobStatus) -> Self:
        return cls(
            id=model.id,
            name=model.name,
        )
