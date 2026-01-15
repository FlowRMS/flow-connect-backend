"""Service layer for Submittals business logic."""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalEmail,
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
    SubmittalRevision,
    SubmittalStakeholder,
    SubmittalStatus,
)
from loguru import logger

from app.graphql.campaigns.services.email_provider_service import EmailProviderService
from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalItemsRepository,
    SubmittalsRepository,
    SubmittalStakeholdersRepository,
)
from app.graphql.submittals.services.pdf_generation_service import (
    PdfGenerationService,
)
from app.graphql.submittals.services.types import SendSubmittalEmailResult
from app.graphql.submittals.strawberry.submittal_input import (
    CreateSubmittalInput,
    GenerateSubmittalPdfInput,
    SendSubmittalEmailInput,
    SubmittalItemInput,
    SubmittalStakeholderInput,
    UpdateSubmittalInput,
    UpdateSubmittalItemInput,
)


@dataclass
class GenerateSubmittalPdfResult:
    """Result of generating a submittal PDF."""

    success: bool = False
    error: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_file_name: Optional[str] = None
    pdf_file_size_bytes: int = 0
    revision: Optional[SubmittalRevision] = None


class SubmittalsService:
    """Service for Submittals business logic."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SubmittalsRepository,
        items_repository: SubmittalItemsRepository,
        stakeholders_repository: SubmittalStakeholdersRepository,
        email_provider: EmailProviderService,
        pdf_service: Optional[PdfGenerationService] = None,
    ) -> None:
        """
        Initialize the Submittals service.

        Args:
            repository: Submittals repository instance
            items_repository: SubmittalItems repository instance
            stakeholders_repository: SubmittalStakeholders repository instance
            email_provider: Email provider service for sending emails
            pdf_service: PDF generation service (optional, created if not provided)
        """
        self.repository = repository
        self.items_repository = items_repository
        self.stakeholders_repository = stakeholders_repository
        self.email_provider = email_provider
        self.pdf_service = pdf_service or PdfGenerationService()

    async def create_submittal(self, input_data: CreateSubmittalInput) -> Submittal:
        """
        Create a new submittal.

        Args:
            input_data: Submittal creation data

        Returns:
            Created Submittal model
        """
        submittal = input_data.to_orm_model()
        created = await self.repository.create(submittal)
        logger.info(
            f"Created submittal {created.id} with number {created.submittal_number}"
        )
        return created

    async def update_submittal(
        self, submittal_id: UUID, input_data: UpdateSubmittalInput
    ) -> Submittal:
        """
        Update an existing submittal.

        Args:
            submittal_id: UUID of the submittal to update
            input_data: Update data

        Returns:
            Updated Submittal model

        Raises:
            ValueError: If submittal not found
        """
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

        updated = await self.repository.update(submittal)
        logger.info(f"Updated submittal {submittal_id}")
        return updated

    async def delete_submittal(self, submittal_id: UUID) -> bool:
        """
        Delete a submittal.

        Args:
            submittal_id: UUID of the submittal to delete

        Returns:
            True if deleted successfully
        """
        result = await self.repository.delete(submittal_id)
        if result:
            logger.info(f"Deleted submittal {submittal_id}")
        return result

    async def get_submittal(self, submittal_id: UUID) -> Optional[Submittal]:
        """
        Get a submittal by ID.

        Args:
            submittal_id: UUID of the submittal

        Returns:
            Submittal model or None if not found
        """
        return await self.repository.get_by_id_with_relations(submittal_id)

    async def get_submittals_by_quote(self, quote_id: UUID) -> list[Submittal]:
        """
        Get all submittals for a quote.

        Args:
            quote_id: UUID of the quote

        Returns:
            List of Submittal models
        """
        return await self.repository.find_by_quote(quote_id)

    async def get_submittals_by_job(self, job_id: UUID) -> list[Submittal]:
        """
        Get all submittals for a job.

        Args:
            job_id: UUID of the job

        Returns:
            List of Submittal models
        """
        return await self.repository.find_by_job(job_id)

    async def search_submittals(
        self,
        search_term: str = "",
        status: Optional[SubmittalStatus] = None,
        limit: int = 50,
    ) -> list[Submittal]:
        """
        Search submittals.

        Args:
            search_term: Search term for submittal_number
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of matching Submittal models
        """
        return await self.repository.search_submittals(search_term, status, limit)

    # Item operations
    async def add_item(
        self, submittal_id: UUID, input_data: SubmittalItemInput
    ) -> SubmittalItem:
        """
        Add an item to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input_data: Item data

        Returns:
            Created SubmittalItem
        """
        item = input_data.to_orm_model()
        created = await self.repository.add_item(submittal_id, item)
        logger.info(f"Added item {created.id} to submittal {submittal_id}")
        return created

    async def update_item(
        self, item_id: UUID, input_data: UpdateSubmittalItemInput
    ) -> SubmittalItem:
        """
        Update a submittal item.

        Args:
            item_id: UUID of the item to update
            input_data: Update data

        Returns:
            Updated SubmittalItem

        Raises:
            ValueError: If item not found
        """
        item = await self.items_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"SubmittalItem with id {item_id} not found")

        if input_data.spec_sheet_id is not None:
            item.spec_sheet_id = input_data.spec_sheet_id

        if input_data.highlight_version_id is not None:
            item.highlight_version_id = input_data.highlight_version_id

        if input_data.part_number is not None:
            item.part_number = input_data.part_number

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

        if input_data.notes is not None:
            item.notes = input_data.notes

        updated = await self.items_repository.update(item)
        logger.info(f"Updated submittal item {item_id}")
        return updated

    async def remove_item(self, item_id: UUID) -> bool:
        """
        Remove an item from a submittal.

        Args:
            item_id: UUID of the item to remove

        Returns:
            True if removed successfully
        """
        result = await self.items_repository.delete(item_id)
        if result:
            logger.info(f"Removed submittal item {item_id}")
        return result

    # Stakeholder operations
    async def add_stakeholder(
        self, submittal_id: UUID, input_data: SubmittalStakeholderInput
    ) -> SubmittalStakeholder:
        """
        Add a stakeholder to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input_data: Stakeholder data

        Returns:
            Created SubmittalStakeholder
        """
        stakeholder = input_data.to_orm_model()
        created = await self.repository.add_stakeholder(submittal_id, stakeholder)
        logger.info(f"Added stakeholder {created.id} to submittal {submittal_id}")
        return created

    async def remove_stakeholder(self, stakeholder_id: UUID) -> bool:
        """
        Remove a stakeholder from a submittal.

        Args:
            stakeholder_id: UUID of the stakeholder to remove

        Returns:
            True if removed successfully
        """
        result = await self.stakeholders_repository.delete(stakeholder_id)
        if result:
            logger.info(f"Removed stakeholder {stakeholder_id}")
        return result

    # Revision operations
    async def create_revision(
        self, submittal_id: UUID, notes: Optional[str] = None
    ) -> SubmittalRevision:
        """
        Create a new revision for a submittal.

        Args:
            submittal_id: UUID of the submittal
            notes: Optional notes for the revision

        Returns:
            Created SubmittalRevision
        """
        next_revision = await self.repository.get_next_revision_number(submittal_id)

        revision = SubmittalRevision(
            revision_number=next_revision,
            notes=notes,
        )

        created = await self.repository.add_revision(submittal_id, revision)
        logger.info(
            f"Created revision {created.revision_number} for submittal {submittal_id}"
        )
        return created

    # Email operations
    async def send_email(
        self, input_data: SendSubmittalEmailInput
    ) -> SendSubmittalEmailResult:
        """
        Send an email for a submittal and record it in the database.

        This method:
        1. Checks if the user has an email provider connected
        2. Sends the email via O365 or Gmail
        3. Records the email in the database

        Args:
            input_data: Email data including recipients, subject, and body

        Returns:
            SendSubmittalEmailResult with email record and send status
        """
        # Check if user has an email provider connected
        has_provider = await self.email_provider.has_connected_provider()
        if not has_provider:
            logger.warning(f"Cannot send submittal email: no email provider connected")
            return SendSubmittalEmailResult(
                success=False,
                error="No email provider connected. Please connect O365 or Gmail in settings.",
            )

        # Send the email
        send_result = await self.email_provider.send_email(
            to=input_data.recipient_emails,
            subject=input_data.subject,
            body=input_data.body or "",
            body_type="HTML",
        )

        if not send_result.success:
            logger.error(f"Failed to send submittal email: {send_result.error}")
            return SendSubmittalEmailResult(
                success=False,
                error=send_result.error,
                send_result=send_result,
            )

        # Record the email in the database
        email = SubmittalEmail(
            revision_id=input_data.revision_id,
            subject=input_data.subject,
            body=input_data.body,
            recipient_emails=input_data.recipient_emails,
            recipients=[
                {"email": e, "type": "to"} for e in input_data.recipient_emails
            ],
        )

        created = await self.repository.add_email(input_data.submittal_id, email)
        logger.info(
            f"Sent and recorded email for submittal {input_data.submittal_id} "
            f"to {len(input_data.recipient_emails)} recipients via {send_result.provider}"
        )

        return SendSubmittalEmailResult(
            email_record=created,
            send_result=send_result,
            success=True,
        )

    # PDF Generation operations
    async def generate_pdf(
        self, input_data: GenerateSubmittalPdfInput
    ) -> GenerateSubmittalPdfResult:
        """
        Generate a PDF for a submittal.

        This method:
        1. Fetches the submittal with all relations
        2. Generates the PDF using the PDF service
        3. Optionally creates a new revision
        4. Returns a URL to download the PDF

        Args:
            input_data: PDF generation options

        Returns:
            GenerateSubmittalPdfResult with PDF URL and metadata
        """
        # Get submittal with all relations
        submittal = await self.repository.get_by_id_with_relations(
            input_data.submittal_id
        )
        if not submittal:
            logger.warning(f"Submittal {input_data.submittal_id} not found for PDF gen")
            return GenerateSubmittalPdfResult(
                success=False,
                error=f"Submittal with id {input_data.submittal_id} not found",
            )

        # TODO: Fetch spec sheet PDFs for items that have them
        # This would need integration with the spec sheets service/S3
        spec_sheet_pdfs: dict = {}

        # Generate the PDF
        pdf_result = await self.pdf_service.generate_submittal_pdf(
            submittal=submittal,
            input_data=input_data,
            spec_sheet_pdfs=spec_sheet_pdfs,
        )

        if not pdf_result.success:
            logger.error(
                f"Failed to generate PDF for submittal {input_data.submittal_id}: "
                f"{pdf_result.error}"
            )
            return GenerateSubmittalPdfResult(
                success=False,
                error=pdf_result.error,
            )

        # TODO: Upload PDF to S3 and get URL
        # For now, we'll encode as base64 data URL for simplicity
        import base64

        pdf_base64 = base64.b64encode(pdf_result.pdf_bytes or b"").decode("utf-8")
        pdf_url = f"data:application/pdf;base64,{pdf_base64}"

        # Create revision if requested
        revision = None
        if input_data.create_revision:
            revision = await self.create_revision(
                submittal_id=input_data.submittal_id,
                notes=input_data.revision_notes or "PDF generated",
            )
            logger.info(
                f"Created revision {revision.revision_number} for submittal "
                f"{input_data.submittal_id} after PDF generation"
            )

        logger.info(
            f"Generated PDF for submittal {input_data.submittal_id}: "
            f"{pdf_result.file_size_bytes} bytes"
        )

        return GenerateSubmittalPdfResult(
            success=True,
            pdf_url=pdf_url,
            pdf_file_name=pdf_result.file_name,
            pdf_file_size_bytes=pdf_result.file_size_bytes,
            revision=revision,
        )
