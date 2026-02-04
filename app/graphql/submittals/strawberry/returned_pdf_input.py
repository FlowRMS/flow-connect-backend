from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import (
    SubmittalChangeAnalysis,
    SubmittalItemChange,
    SubmittalReturnedPdf,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    ChangeAnalysisSourceGQL,
    ItemChangeStatusGQL,
    OverallChangeStatusGQL,
)


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


@strawberry.input
class CreateChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    """Input for creating a change analysis."""

    returned_pdf_id: UUID
    analyzed_by: ChangeAnalysisSourceGQL = ChangeAnalysisSourceGQL.MANUAL
    overall_status: OverallChangeStatusGQL = OverallChangeStatusGQL.APPROVED
    summary: str | None = None


@strawberry.input
class UpdateChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    """Input for updating a change analysis."""

    overall_status: OverallChangeStatusGQL | None = None
    summary: str | None = None


@strawberry.input
class AddItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    """Input for adding an item change to a change analysis."""

    change_analysis_id: UUID
    fixture_type: str
    catalog_number: str
    manufacturer: str
    item_id: UUID | None = None
    status: ItemChangeStatusGQL = ItemChangeStatusGQL.APPROVED
    notes: list[str] | None = None
    page_references: list[int] | None = None


@strawberry.input
class UpdateItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    """Input for updating an item change."""

    status: ItemChangeStatusGQL | None = None
    notes: list[str] | None = None
    page_references: list[int] | None = None
    resolved: bool | None = None
