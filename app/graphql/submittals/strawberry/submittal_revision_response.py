from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalRevision
from sqlalchemy import inspect

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.send_email_response import (
    SubmittalEmailResponse,
)
from app.graphql.submittals.strawberry.submittal_returned_pdf_response import (
    SubmittalReturnedPdfResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SubmittalRevisionResponse(DTOMixin[SubmittalRevision]):
    """Response type for SubmittalRevision."""

    _instance: strawberry.Private[SubmittalRevision]
    _created_by_response: strawberry.Private[UserResponse | None]
    _emails_response: strawberry.Private[list[SubmittalEmailResponse]]
    _returned_pdfs_response: strawberry.Private[list[SubmittalReturnedPdfResponse]]
    id: UUID
    submittal_id: UUID
    revision_number: int
    pdf_file_id: UUID | None
    pdf_file_url: str | None
    pdf_file_name: str | None
    pdf_file_size_bytes: int | None
    notes: str | None
    created_at: datetime
    created_by_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: SubmittalRevision) -> Self:
        """Convert ORM model to GraphQL response."""
        state = inspect(model)

        # Extract created_by
        created_by_response: UserResponse | None = None
        if "created_by" not in state.unloaded and model.created_by is not None:
            created_by_response = UserResponse.from_orm_model(model.created_by)

        # Extract emails
        emails_response: list[SubmittalEmailResponse] = []
        if "emails" not in state.unloaded and model.emails:
            emails_response = [
                SubmittalEmailResponse.from_orm_model(email) for email in model.emails
            ]

        # Extract returned_pdfs
        returned_pdfs_response: list[SubmittalReturnedPdfResponse] = []
        if "returned_pdfs" not in state.unloaded and model.returned_pdfs:
            returned_pdfs_response = [
                SubmittalReturnedPdfResponse.from_orm_model(pdf)
                for pdf in model.returned_pdfs
            ]

        return cls(
            _instance=model,
            _created_by_response=created_by_response,
            _emails_response=emails_response,
            _returned_pdfs_response=returned_pdfs_response,
            id=model.id,
            submittal_id=model.submittal_id,
            revision_number=model.revision_number,
            pdf_file_id=model.pdf_file_id,
            pdf_file_url=model.pdf_file_url,
            pdf_file_name=model.pdf_file_name,
            pdf_file_size_bytes=model.pdf_file_size_bytes,
            notes=model.notes,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )

    @strawberry.field
    def created_by(self) -> UserResponse | None:
        """Resolve created_by from cached response."""
        return self._created_by_response

    @strawberry.field
    def emails_sent(self) -> list[SubmittalEmailResponse]:
        """Resolve emails from cached response."""
        return self._emails_response

    @strawberry.field
    def returned_pdfs(self) -> list[SubmittalReturnedPdfResponse]:
        """Resolve returned_pdfs from cached response."""
        return self._returned_pdfs_response
