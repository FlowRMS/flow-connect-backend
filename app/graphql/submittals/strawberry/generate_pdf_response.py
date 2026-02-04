from typing import Self

import strawberry
from commons.db.v6.crm.submittals import SubmittalRevision

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.submittal_revision_response import (
    SubmittalRevisionResponse,
)


@strawberry.type
class GenerateSubmittalPdfResponse(DTOMixin[SubmittalRevision]):
    """Response type for generate submittal PDF mutation."""

    success: bool
    error: str | None = None
    pdf_url: str | None = None
    pdf_file_name: str | None = None
    pdf_file_size_bytes: int | None = None
    revision: SubmittalRevisionResponse | None = None
    email_sent: bool = False
    email_recipients_count: int = 0

    @classmethod
    def success_response(
        cls,
        pdf_url: str,
        pdf_file_name: str,
        pdf_file_size_bytes: int,
        revision: SubmittalRevisionResponse | None = None,
        email_sent: bool = False,
        email_recipients_count: int = 0,
    ) -> Self:
        """Create a success response."""
        return cls(
            success=True,
            pdf_url=pdf_url,
            pdf_file_name=pdf_file_name,
            pdf_file_size_bytes=pdf_file_size_bytes,
            revision=revision,
            email_sent=email_sent,
            email_recipients_count=email_recipients_count,
        )

    @classmethod
    def error_response(cls, error: str) -> Self:
        """Create an error response."""
        return cls(
            success=False,
            error=error,
        )

    @classmethod
    def from_orm_model(cls, model: SubmittalRevision) -> Self:
        """Create response from ORM model (partial - use factory methods for full response)."""
        return cls(
            success=True,
            revision=SubmittalRevisionResponse.from_orm_model(model),
        )
