from uuid import UUID

from commons.db.v6.crm.submittals import (
    ItemChangeStatus,
    SubmittalChangeAnalysis,
    SubmittalItemChange,
    SubmittalReturnedPdf,
)
from loguru import logger

from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalChangeAnalysisRepository,
    SubmittalItemChangesRepository,
    SubmittalReturnedPdfsRepository,
    SubmittalRevisionsRepository,
)
from app.graphql.submittals.strawberry.add_change_analysis_input import (
    AddChangeAnalysisInput,
)
from app.graphql.submittals.strawberry.add_returned_pdf_input import AddReturnedPdfInput
from app.graphql.submittals.strawberry.update_item_change_input import (
    UpdateItemChangeInput,
)


class SubmittalsChangeService:
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

    async def add_returned_pdf(
        self, input_data: AddReturnedPdfInput
    ) -> SubmittalReturnedPdf:
        returned_pdf = input_data.to_orm_model()
        created = await self.revisions_repository.add_returned_pdf(
            input_data.revision_id, returned_pdf
        )
        logger.info(
            f"Added returned PDF {created.id} to revision {input_data.revision_id}"
        )
        return created

    async def add_change_analysis(
        self, input_data: AddChangeAnalysisInput
    ) -> SubmittalChangeAnalysis:
        change_analysis = input_data.to_orm_model()
        created = await self.returned_pdfs_repository.add_change_analysis(
            input_data.returned_pdf_id, change_analysis
        )
        logger.info(
            f"Added change analysis {created.id} to returned PDF "
            f"{input_data.returned_pdf_id}"
        )
        return created

    async def update_item_change(
        self, item_change_id: UUID, input_data: UpdateItemChangeInput
    ) -> SubmittalItemChange:
        item_change = await self.item_changes_repository.get_by_id(item_change_id)
        if not item_change:
            raise ValueError(f"SubmittalItemChange with id {item_change_id} not found")

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
            raise ValueError(f"SubmittalItemChange with id {item_change_id} not found")

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
            raise ValueError(f"SubmittalItemChange with id {item_change_id} not found")

        item_change.resolved = True
        updated = await self.item_changes_repository.update(item_change)
        logger.info(f"Resolved item change {item_change_id}")
        return updated
