from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalReturnedPdf

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class UploadReturnedPdfInput(BaseInputGQL[SubmittalReturnedPdf]):
    """Input for uploading a returned PDF."""

    revision_id: UUID
    file_name: str
    file_url: str
    file_size: int = 0
    file_id: UUID | None = None  # Reference to files table for presigned URL generation
    returned_by_stakeholder_id: UUID | None = None
    received_date: date | None = None
    notes: str | None = None
