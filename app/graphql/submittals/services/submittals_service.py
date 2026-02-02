from uuid import UUID

from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalChangeAnalysis,
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemChange,
    SubmittalItemMatchStatus,
    SubmittalReturnedPdf,
    SubmittalRevision,
    SubmittalStakeholder,
    SubmittalStatus,
)
from loguru import logger
from strawberry import UNSET

from app.graphql.campaigns.services.email_provider_service import EmailProviderService
from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalChangeAnalysisRepository,
    SubmittalItemChangesRepository,
    SubmittalItemsRepository,
    SubmittalReturnedPdfsRepository,
    SubmittalRevisionsRepository,
    SubmittalsRepository,
    SubmittalStakeholdersRepository,
)
from app.graphql.submittals.services.submittal_pdf_export_service import (
    SubmittalPdfExportService,
)
from app.graphql.submittals.services.submittals_change_service import (
    SubmittalsChangeService,
)
from app.graphql.submittals.services.submittals_email_service import (
    SubmittalsEmailService,
)
from app.graphql.submittals.services.submittals_revision_service import (
    GenerateSubmittalPdfResult,
    SubmittalsRevisionService,
)
from app.graphql.submittals.services.types import SendSubmittalEmailResult
from app.graphql.submittals.strawberry.submittal_input import (
    AddChangeAnalysisInput,
    AddReturnedPdfInput,
    CreateSubmittalInput,
    GenerateSubmittalPdfInput,
    SendSubmittalEmailInput,
    SubmittalItemInput,
    SubmittalStakeholderInput,
    UpdateItemChangeInput,
    UpdateSubmittalInput,
    UpdateSubmittalItemInput,
)

# Re-export for backward compatibility
__all__ = [
    "GenerateSubmittalPdfResult",
    "SendSubmittalEmailResult",
    "SubmittalsService",
]


class SubmittalsService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SubmittalsRepository,
        items_repository: SubmittalItemsRepository,
        stakeholders_repository: SubmittalStakeholdersRepository,
        revisions_repository: SubmittalRevisionsRepository,
        returned_pdfs_repository: SubmittalReturnedPdfsRepository,
        change_analysis_repository: SubmittalChangeAnalysisRepository,
        item_changes_repository: SubmittalItemChangesRepository,
        email_provider: EmailProviderService,
        pdf_export_service: SubmittalPdfExportService,
    ) -> None:
        self.repository = repository
        self.items_repository = items_repository
        self.stakeholders_repository = stakeholders_repository

        self._email_service = SubmittalsEmailService(repository, email_provider)
        self._revision_service = SubmittalsRevisionService(
            repository, pdf_export_service, self._email_service
        )
        self._change_service = SubmittalsChangeService(
            revisions_repository,
            returned_pdfs_repository,
            change_analysis_repository,
            item_changes_repository,
        )

    async def create_submittal(self, input_data: CreateSubmittalInput) -> Submittal:
        submittal = input_data.to_orm_model()
        created = await self.repository.create(submittal)
        logger.info(
            f"Created submittal {created.id} with number {created.submittal_number}"
        )
        submittal_with_relations = await self.repository.get_by_id_with_relations(
            created.id
        )
        return submittal_with_relations or created

    async def update_submittal(
        self, submittal_id: UUID, input_data: UpdateSubmittalInput
    ) -> Submittal:
        submittal = await self.repository.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        if input_data.status is not None:
            submittal.status = SubmittalStatus(input_data.status.value)

        if input_data.transmittal_purpose is not None:
            from commons.db.v6.crm.submittals import TransmittalPurpose

            submittal.transmittal_purpose = TransmittalPurpose(
                input_data.transmittal_purpose.value
            )

        if input_data.description is not None:
            submittal.description = input_data.description
        if input_data.job_location is not None:
            submittal.job_location = input_data.job_location
        if input_data.bid_date is not None:
            submittal.bid_date = input_data.bid_date
        if input_data.tags is not None:
            submittal.tags = input_data.tags

        if input_data.config is not None:
            config = input_data.config
            submittal.config_include_lamps = config.include_lamps
            submittal.config_include_accessories = config.include_accessories
            submittal.config_include_cq = config.include_cq
            submittal.config_include_from_orders = config.include_from_orders
            submittal.config_roll_up_kits = config.roll_up_kits
            submittal.config_roll_up_accessories = config.roll_up_accessories
            submittal.config_include_zero_quantity_items = (
                config.include_zero_quantity_items
            )
            submittal.config_drop_descriptions = config.drop_descriptions
            submittal.config_drop_line_notes = config.drop_line_notes

        updated = await self.repository.update(submittal)
        logger.info(f"Updated submittal {submittal_id}")
        return updated

    async def delete_submittal(self, submittal_id: UUID) -> bool:
        result = await self.repository.delete(submittal_id)
        if result:
            logger.info(f"Deleted submittal {submittal_id}")
        return result

    async def get_submittal(self, submittal_id: UUID) -> Submittal | None:
        return await self.repository.get_by_id_with_relations(submittal_id)

    async def get_submittals_by_quote(self, quote_id: UUID) -> list[Submittal]:
        return await self.repository.find_by_quote(quote_id)

    async def get_submittals_by_job(self, job_id: UUID) -> list[Submittal]:
        return await self.repository.find_by_job(job_id)

    async def search_submittals(
        self,
        search_term: str = "",
        status: SubmittalStatus | None = None,
        limit: int = 50,
    ) -> list[Submittal]:
        return await self.repository.search_submittals(search_term, status, limit)

    async def add_item(
        self, submittal_id: UUID, input_data: SubmittalItemInput
    ) -> SubmittalItem:
        item = input_data.to_orm_model()

        if item.spec_sheet_id and item.highlight_version_id:
            item.match_status = SubmittalItemMatchStatus.EXACT_MATCH
        elif item.spec_sheet_id:
            item.match_status = SubmittalItemMatchStatus.PARTIAL_MATCH
        else:
            item.match_status = SubmittalItemMatchStatus.NO_MATCH

        created = await self.repository.add_item(submittal_id, item)
        logger.info(f"Added item {created.id} to submittal {submittal_id}")
        item_with_relations = await self.items_repository.get_by_id_with_relations(
            created.id
        )
        return item_with_relations or created

    async def update_item(
        self, item_id: UUID, input_data: UpdateSubmittalItemInput
    ) -> SubmittalItem:
        item = await self.items_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"SubmittalItem with id {item_id} not found")

        if input_data.spec_sheet_id is not UNSET:
            item.spec_sheet_id = input_data.spec_sheet_id
        if input_data.highlight_version_id is not UNSET:
            item.highlight_version_id = input_data.highlight_version_id
        if input_data.part_number is not None:
            item.part_number = input_data.part_number
        if input_data.manufacturer is not None:
            item.manufacturer = input_data.manufacturer
        if input_data.description is not None:
            item.description = input_data.description
        if input_data.quantity is not None:
            item.quantity = input_data.quantity
        if input_data.approval_status is not None:
            item.approval_status = SubmittalItemApprovalStatus(
                input_data.approval_status.value
            )
        if input_data.match_status is not None:
            item.match_status = SubmittalItemMatchStatus(input_data.match_status.value)
        else:
            if item.spec_sheet_id and item.highlight_version_id:
                item.match_status = SubmittalItemMatchStatus.EXACT_MATCH
            elif item.spec_sheet_id:
                item.match_status = SubmittalItemMatchStatus.PARTIAL_MATCH
            else:
                item.match_status = SubmittalItemMatchStatus.NO_MATCH
        if input_data.notes is not None:
            item.notes = input_data.notes

        updated = await self.items_repository.update(item)
        logger.info(f"Updated submittal item {item_id}")
        item_with_relations = await self.items_repository.get_by_id_with_relations(
            updated.id
        )
        return item_with_relations or updated

    async def remove_item(self, item_id: UUID) -> bool:
        result = await self.items_repository.delete(item_id)
        if result:
            logger.info(f"Removed submittal item {item_id}")
        return result

    async def add_stakeholder(
        self, submittal_id: UUID, input_data: SubmittalStakeholderInput
    ) -> SubmittalStakeholder:
        stakeholder = input_data.to_orm_model()
        created = await self.repository.add_stakeholder(submittal_id, stakeholder)
        logger.info(f"Added stakeholder {created.id} to submittal {submittal_id}")
        return created

    async def remove_stakeholder(self, stakeholder_id: UUID) -> bool:
        result = await self.stakeholders_repository.delete(stakeholder_id)
        if result:
            logger.info(f"Removed stakeholder {stakeholder_id}")
        return result

    # Delegated to revision service
    async def create_revision(
        self,
        submittal_id: UUID,
        notes: str | None = None,
        pdf_file_id: UUID | None = None,
        pdf_file_url: str | None = None,
        pdf_file_name: str | None = None,
        pdf_file_size_bytes: int | None = None,
    ) -> SubmittalRevision:
        return await self._revision_service.create_revision(
            submittal_id,
            notes,
            pdf_file_id,
            pdf_file_url,
            pdf_file_name,
            pdf_file_size_bytes,
        )

    async def generate_pdf(
        self, input_data: GenerateSubmittalPdfInput
    ) -> GenerateSubmittalPdfResult:
        return await self._revision_service.generate_pdf(input_data)

    # Delegated to email service
    async def send_email(
        self, input_data: SendSubmittalEmailInput
    ) -> SendSubmittalEmailResult:
        return await self._email_service.send_email(input_data)

    # Delegated to change service
    async def add_returned_pdf(
        self, input_data: AddReturnedPdfInput
    ) -> SubmittalReturnedPdf:
        return await self._change_service.add_returned_pdf(input_data)

    async def add_change_analysis(
        self, input_data: AddChangeAnalysisInput
    ) -> SubmittalChangeAnalysis:
        return await self._change_service.add_change_analysis(input_data)

    async def update_item_change(
        self, item_change_id: UUID, input_data: UpdateItemChangeInput
    ) -> SubmittalItemChange:
        return await self._change_service.update_item_change(item_change_id, input_data)

    async def delete_item_change(self, item_change_id: UUID) -> bool:
        return await self._change_service.delete_item_change(item_change_id)

    async def resolve_item_change(self, item_change_id: UUID) -> SubmittalItemChange:
        return await self._change_service.resolve_item_change(item_change_id)
