"""GraphQL response type for SubmittalRevision."""

from datetime import datetime
from typing import Optional, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalRevision

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SubmittalRevisionResponse(DTOMixin[SubmittalRevision]):
    """Response type for SubmittalRevision."""

    _instance: strawberry.Private[SubmittalRevision]
    id: UUID
    submittal_id: UUID
    revision_number: int
    pdf_file_id: Optional[UUID]
    pdf_file_url: Optional[str]
    pdf_file_name: Optional[str]
    notes: Optional[str]
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SubmittalRevision) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            submittal_id=model.submittal_id,
            revision_number=model.revision_number,
            pdf_file_id=model.pdf_file_id,
            pdf_file_url=model.pdf_file_url,
            pdf_file_name=model.pdf_file_name,
            notes=model.notes,
            created_at=model.created_at,
        )

    @strawberry.field
    def created_by(self) -> UserResponse:
        """Resolve created_by from the ORM instance."""
        return UserResponse.from_orm_model(self._instance.created_by)
