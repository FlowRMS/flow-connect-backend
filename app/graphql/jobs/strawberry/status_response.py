"""Strawberry GraphQL response types for Status entity."""

import uuid
from typing import Self

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.jobs.models.status_model import JobStatus


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
