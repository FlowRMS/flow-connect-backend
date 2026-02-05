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
from app.graphql.submittals.strawberry.add_item_change_input import AddItemChangeInput
from app.graphql.submittals.strawberry.create_change_analysis_input import (
    CreateChangeAnalysisInput,
)
from app.graphql.submittals.strawberry.update_change_analysis_input import (
    UpdateChangeAnalysisInput,
)
from app.graphql.submittals.strawberry.update_item_change_input import (
    UpdateItemChangeInput,
)
from app.graphql.submittals.strawberry.upload_returned_pdf_input import (
    UploadReturnedPdfInput,
)


class ReturnedPdfService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        revisions_repository: SubmittalRevisionsRepository,
        returned_pdfs_repository: SubmittalReturnedPdfsRepository,
        change_analysis_repository: SubmittalChangeAnalysisRepository,
        item_changes_repository: SubmittalItemChangesRepository,
    ) -> None:
        self.revisions_repository = revisions_repository
        self.returned_pdfs_repository = returned_pdfs_repository
        self.change_analysis_repository = change_analysis_repository
        self.item_changes_repository = item_changes_repository

    async def upload_returned_pdf(
        self, input_data: UploadReturnedPdfInput
    ) -> SubmittalReturnedPdf:
        returned_pdf = SubmittalReturnedPdf(
            file_name=input_data.file_name,
            file_url=input_data.file_url,
            file_size=input_data.file_size,
            file_id=input_data.file_id,
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
        return await self.returned_pdfs_repository.get_by_id_with_analysis(
            returned_pdf_id
        )

    async def delete_returned_pdf(self, returned_pdf_id: UUID) -> bool:
        result = await self.returned_pdfs_repository.delete(returned_pdf_id)
        if result:
            logger.info(f"Deleted returned PDF {returned_pdf_id}")
        return result

    async def get_revision_with_returned_pdfs(
        self, revision_id: UUID
    ) -> SubmittalRevision | None:
        return await self.revisions_repository.get_by_id_with_returned_pdfs(revision_id)

    async def create_change_analysis(
        self, input_data: CreateChangeAnalysisInput
    ) -> SubmittalChangeAnalysis:
        change_analysis = SubmittalChangeAnalysis(
            analyzed_by=ChangeAnalysisSource(input_data.analyzed_by.value),
            overall_status=OverallChangeStatus(input_data.overall_status.value),
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
        return await self.change_analysis_repository.get_by_id_with_item_changes(
            analysis_id
        )

    async def update_change_analysis(
        self,
        analysis_id: UUID,
        input_data: UpdateChangeAnalysisInput,
    ) -> SubmittalChangeAnalysis:
        analysis = await self.change_analysis_repository.get_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"ChangeAnalysis with id {analysis_id} not found")

        overall_status = input_data.optional_field(input_data.overall_status)
        if overall_status is not None:
            analysis.overall_status = OverallChangeStatus(overall_status.value)
        summary = input_data.optional_field(input_data.summary)
        if summary is not None:
            analysis.summary = summary

        updated = await self.change_analysis_repository.update(analysis)
        logger.info(f"Updated change analysis {analysis_id}")
        return updated

    async def delete_change_analysis(self, analysis_id: UUID) -> bool:
        result = await self.change_analysis_repository.delete(analysis_id)
        if result:
            logger.info(f"Deleted change analysis {analysis_id}")
        return result

    async def add_item_change(
        self, input_data: AddItemChangeInput
    ) -> SubmittalItemChange:
        item_change = SubmittalItemChange(
            fixture_type=input_data.fixture_type,
            catalog_number=input_data.catalog_number,
            manufacturer=input_data.manufacturer,
            item_id=input_data.item_id,
            status=ItemChangeStatus(input_data.status.value),
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
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            raise ValueError(f"ItemChange with id {item_change_id} not found")

        status = input_data.optional_field(input_data.status)
        if status is not None:
            item_change.status = ItemChangeStatus(status.value)
        notes = input_data.optional_field(input_data.notes)
        if notes is not None:
            item_change.notes = notes
        page_references = input_data.optional_field(input_data.page_references)
        if page_references is not None:
            item_change.page_references = page_references
        resolved = input_data.optional_field(input_data.resolved)
        if resolved is not None:
            item_change.resolved = resolved
        fixture_type = input_data.optional_field(input_data.fixture_type)
        if fixture_type is not None:
            item_change.fixture_type = fixture_type
        catalog_number = input_data.optional_field(input_data.catalog_number)
        if catalog_number is not None:
            item_change.catalog_number = catalog_number
        manufacturer = input_data.optional_field(input_data.manufacturer)
        if manufacturer is not None:
            item_change.manufacturer = manufacturer

        updated = await self.item_changes_repository.update(item_change)
        logger.info(f"Updated item change {item_change_id}")
        return updated

    async def delete_item_change(self, item_change_id: UUID) -> bool:
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            return False

        analysis_id = item_change.change_analysis_id

        result = await self.item_changes_repository.delete(item_change_id)
        if result:
            analysis = await self.change_analysis_repository.get_by_id(analysis_id)
            if analysis:
                analysis.total_changes_detected = max(
                    0, analysis.total_changes_detected - 1
                )
                _ = await self.change_analysis_repository.update(analysis)
            logger.info(f"Deleted item change {item_change_id}")
        return result

    async def resolve_item_change(self, item_change_id: UUID) -> SubmittalItemChange:
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            raise ValueError(f"ItemChange with id {item_change_id} not found")

        item_change.resolved = True
        updated = await self.item_changes_repository.update(item_change)
        logger.info(f"Resolved item change {item_change_id}")
        return updated
