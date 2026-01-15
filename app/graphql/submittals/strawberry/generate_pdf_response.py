"""GraphQL response type for generating submittal PDFs."""

from typing import Optional, Self

import strawberry

from app.graphql.submittals.strawberry.submittal_revision_response import (
    SubmittalRevisionResponse,
)


@strawberry.type
class GenerateSubmittalPdfResponse:
    """Response type for generate submittal PDF mutation."""

    success: bool
    error: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_file_name: Optional[str] = None
    pdf_file_size_bytes: Optional[int] = None
    revision: Optional[SubmittalRevisionResponse] = None

    @classmethod
    def success_response(
        cls,
        pdf_url: str,
        pdf_file_name: str,
        pdf_file_size_bytes: int,
        revision: Optional[SubmittalRevisionResponse] = None,
    ) -> Self:
        """Create a success response."""
        return cls(
            success=True,
            pdf_url=pdf_url,
            pdf_file_name=pdf_file_name,
            pdf_file_size_bytes=pdf_file_size_bytes,
            revision=revision,
        )

    @classmethod
    def error_response(cls, error: str) -> Self:
        """Create an error response."""
        return cls(
            success=False,
            error=error,
        )
