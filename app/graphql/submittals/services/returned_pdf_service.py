from dataclasses import dataclass
from datetime import date
from uuid import UUID

from commons.db.v6.crm.submittals import (
    ChangeAnalysisSource,
    ItemChangeStatus,
    OverallChangeStatus,
    SubmittalChangeAnalysis,
    SubmittalItemChange,
    SubmittalReturnedPdf,
    SubmittalRevision,
)
from loguru import logger

from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalChangeAnalysisRepository,
    SubmittalItemChangesRepository,
    SubmittalReturnedPdfsRepository,
    SubmittalRevisionsRepository,
)


@dataclass
class UploadReturnedPdfInput:
    """Input for uploading a returned PDF."""

    revision_id: UUID
    file_name: str
    file_url: str
    file_size: int = 0
    returned_by_stakeholder_id: UUID | None = None
    received_date: date | None = None
    notes: str | None = None


@dataclass
class CreateChangeAnalysisInput:
    """Input for creating a change analysis."""

    returned_pdf_id: UUID
    analyzed_by: ChangeAnalysisSource = ChangeAnalysisSource.MANUAL
    overall_status: OverallChangeStatus = OverallChangeStatus.APPROVED
    summary: str | None = None


@dataclass
class AddItemChangeInput:
    """Input for adding an item change."""

    change_analysis_id: UUID
    fixture_type: str
    catalog_number: str
    manufacturer: str
    item_id: UUID | None = None
    status: ItemChangeStatus = ItemChangeStatus.APPROVED
    notes: list[str] | None = None
    page_references: list[int] | None = None


@dataclass
class UpdateItemChangeInput:
    """Input for updating an item change."""

    status: ItemChangeStatus | None = None
    notes: list[str] | None = None
    page_references: list[int] | None = None
    resolved: bool | None = None


class ReturnedPdfService:
    """Service for managing returned PDFs and change analysis."""

    def __init__(
        self,
        revisions_repository: SubmittalRevisionsRepository,
        returned_pdfs_repository: SubmittalReturnedPdfsRepository,
        change_analysis_repository: SubmittalChangeAnalysisRepository,
        item_changes_repository: SubmittalItemChangesRepository,
    ) -> None:
        """Initialize the service with repositories."""
        self.revisions_repository = revisions_repository
        self.returned_pdfs_repository = returned_pdfs_repository
        self.change_analysis_repository = change_analysis_repository
        self.item_changes_repository = item_changes_repository

    # Returned PDF operations
    async def upload_returned_pdf(
        self, input_data: UploadReturnedPdfInput
    ) -> SubmittalReturnedPdf:
        """
        Upload a returned PDF to a revision.

        Args:
            input_data: Upload data including file info and optional stakeholder

        Returns:
            Created SubmittalReturnedPdf
        """
        returned_pdf = SubmittalReturnedPdf(
            file_name=input_data.file_name,
            file_url=input_data.file_url,
            file_size=input_data.file_size,
            returned_by_stakeholder_id=input_data.returned_by_stakeholder_id,
            received_date=input_data.received_date,
            notes=input_data.notes,
        )

        created = await self.revisions_repository.add_returned_pdf(
            input_data.revision_id, returned_pdf
        )
        logger.info(
            f"Uploaded returned PDF {created.id} to revision {input_data.revision_id}"
        )
        return created

    async def get_returned_pdf(
        self, returned_pdf_id: UUID
    ) -> SubmittalReturnedPdf | None:
        """Get a returned PDF by ID with change analysis."""
        return await self.returned_pdfs_repository.get_by_id_with_analysis(
            returned_pdf_id
        )

    async def delete_returned_pdf(self, returned_pdf_id: UUID) -> bool:
        """Delete a returned PDF."""
        result = await self.returned_pdfs_repository.delete(returned_pdf_id)
        if result:
            logger.info(f"Deleted returned PDF {returned_pdf_id}")
        return result

    async def get_revision_with_returned_pdfs(
        self, revision_id: UUID
    ) -> SubmittalRevision | None:
        """Get a revision with all returned PDFs loaded."""
        return await self.revisions_repository.get_by_id_with_returned_pdfs(revision_id)

    # Change Analysis operations
    async def create_change_analysis(
        self, input_data: CreateChangeAnalysisInput
    ) -> SubmittalChangeAnalysis:
        """
        Create a change analysis for a returned PDF.

        Args:
            input_data: Analysis data

        Returns:
            Created SubmittalChangeAnalysis
        """
        change_analysis = SubmittalChangeAnalysis(
            analyzed_by=input_data.analyzed_by,
            overall_status=input_data.overall_status,
            summary=input_data.summary,
            total_changes_detected=0,
        )

        created = await self.returned_pdfs_repository.add_change_analysis(
            input_data.returned_pdf_id, change_analysis
        )
        logger.info(
            f"Created change analysis {created.id} for returned PDF "
            f"{input_data.returned_pdf_id}"
        )
        return created

    async def get_change_analysis(
        self, analysis_id: UUID
    ) -> SubmittalChangeAnalysis | None:
        """Get a change analysis by ID with item changes."""
        return await self.change_analysis_repository.get_by_id_with_item_changes(
            analysis_id
        )

    async def update_change_analysis(
        self,
        analysis_id: UUID,
        overall_status: OverallChangeStatus | None = None,
        summary: str | None = None,
    ) -> SubmittalChangeAnalysis:
        """Update a change analysis."""
        analysis = await self.change_analysis_repository.get_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"ChangeAnalysis with id {analysis_id} not found")

        if overall_status is not None:
            analysis.overall_status = overall_status
        if summary is not None:
            analysis.summary = summary

        updated = await self.change_analysis_repository.update(analysis)
        logger.info(f"Updated change analysis {analysis_id}")
        return updated

    async def delete_change_analysis(self, analysis_id: UUID) -> bool:
        """Delete a change analysis."""
        result = await self.change_analysis_repository.delete(analysis_id)
        if result:
            logger.info(f"Deleted change analysis {analysis_id}")
        return result

    # Item Change operations
    async def add_item_change(
        self, input_data: AddItemChangeInput
    ) -> SubmittalItemChange:
        """
        Add an item change to a change analysis.

        Args:
            input_data: Item change data

        Returns:
            Created SubmittalItemChange
        """
        item_change = SubmittalItemChange(
            fixture_type=input_data.fixture_type,
            catalog_number=input_data.catalog_number,
            manufacturer=input_data.manufacturer,
            item_id=input_data.item_id,
            status=input_data.status,
            notes=input_data.notes,
            page_references=input_data.page_references,
            resolved=False,
        )

        created = await self.change_analysis_repository.add_item_change(
            input_data.change_analysis_id, item_change
        )
        logger.info(
            f"Added item change {created.id} to analysis "
            f"{input_data.change_analysis_id}"
        )
        return created

    async def update_item_change(
        self, item_change_id: UUID, input_data: UpdateItemChangeInput
    ) -> SubmittalItemChange:
        """Update an item change."""
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            raise ValueError(f"ItemChange with id {item_change_id} not found")

        if input_data.status is not None:
            item_change.status = input_data.status
        if input_data.notes is not None:
            item_change.notes = input_data.notes
        if input_data.page_references is not None:
            item_change.page_references = input_data.page_references
        if input_data.resolved is not None:
            item_change.resolved = input_data.resolved

        updated = await self.item_changes_repository.update(item_change)
        logger.info(f"Updated item change {item_change_id}")
        return updated

    async def delete_item_change(self, item_change_id: UUID) -> bool:
        """Delete an item change."""
        # Get the item change to find its parent analysis
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            return False

        analysis_id = item_change.change_analysis_id

        # Delete the item change
        result = await self.item_changes_repository.delete(item_change_id)
        if result:
            # Update the total count in the parent analysis
            analysis = await self.change_analysis_repository.get_by_id(analysis_id)
            if analysis:
                analysis.total_changes_detected = max(
                    0, analysis.total_changes_detected - 1
                )
                await self.change_analysis_repository.update(analysis)
            logger.info(f"Deleted item change {item_change_id}")
        return result

    async def resolve_item_change(self, item_change_id: UUID) -> SubmittalItemChange:
        """Mark an item change as resolved."""
        return await self.update_item_change(
            item_change_id, UpdateItemChangeInput(resolved=True)
        )
