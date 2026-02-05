from uuid import UUID

from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalChangeAnalysis,
    SubmittalItem,
    SubmittalItemChange,
    SubmittalReturnedPdf,
    SubmittalRevision,
    SubmittalStakeholder,
    SubmittalStatus,
)
from loguru import logger

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
from app.graphql.submittals.services.submittals_item_service import (
    SubmittalsItemService,
)
from app.graphql.submittals.services.submittals_revision_service import (
    GenerateSubmittalPdfResult,
    SubmittalsRevisionService,
)
from app.graphql.submittals.services.types import SendSubmittalEmailResult
from app.graphql.submittals.strawberry.add_change_analysis_input import (
    AddChangeAnalysisInput,
)
from app.graphql.submittals.strawberry.add_returned_pdf_input import AddReturnedPdfInput
from app.graphql.submittals.strawberry.create_submittal_input import (
    CreateSubmittalInput,
)
from app.graphql.submittals.strawberry.generate_submittal_pdf_input import (
    GenerateSubmittalPdfInput,
)
from app.graphql.submittals.strawberry.send_submittal_email_input import (
    SendSubmittalEmailInput,
)
from app.graphql.submittals.strawberry.submittal_item_input import SubmittalItemInput
from app.graphql.submittals.strawberry.submittal_stakeholder_input import (
    SubmittalStakeholderInput,
)
from app.graphql.submittals.strawberry.update_item_change_input import (
    UpdateItemChangeInput,
)
from app.graphql.submittals.strawberry.update_submittal_input import (
    UpdateSubmittalInput,
)
from app.graphql.submittals.strawberry.update_submittal_item_input import (
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
        self.stakeholders_repository = stakeholders_repository

        self._item_service = SubmittalsItemService(repository, items_repository)
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
            new_status = SubmittalStatus(input_data.status.value)
            if new_status == SubmittalStatus.APPROVED:
                submittal_with_items = await self.repository.get_by_id_with_relations(
                    submittal_id
                )
                if submittal_with_items and submittal_with_items.items:
                    missing_spec_sheets = [
                        item
                        for item in submittal_with_items.items
                        if item.spec_sheet_id is None
                    ]
                    if missing_spec_sheets:
                        raise ValueError(
                            f"Cannot set status to Approved: {len(missing_spec_sheets)} "
                            f"item(s) are missing spec sheets"
                        )
            submittal.status = new_status

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

    # Delegated to item service
    async def add_item(
        self, submittal_id: UUID, input_data: SubmittalItemInput
    ) -> SubmittalItem:
        return await self._item_service.add_item(submittal_id, input_data)

    async def update_item(
        self, item_id: UUID, input_data: UpdateSubmittalItemInput
    ) -> SubmittalItem:
        return await self._item_service.update_item(item_id, input_data)

    async def remove_item(self, item_id: UUID) -> bool:
        return await self._item_service.remove_item(item_id)

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
