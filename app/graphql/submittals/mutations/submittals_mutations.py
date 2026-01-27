from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.submittals.services.submittals_service import SubmittalsService
from app.graphql.submittals.strawberry.generate_pdf_response import (
    GenerateSubmittalPdfResponse,
)
from app.graphql.submittals.strawberry.send_email_response import (
    SendSubmittalEmailResponse,
)
from app.graphql.submittals.strawberry.submittal_change_analysis_response import (
    SubmittalChangeAnalysisResponse,
)
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
from app.graphql.submittals.strawberry.submittal_item_change_response import (
    SubmittalItemChangeResponse,
)
from app.graphql.submittals.strawberry.submittal_item_response import (
    SubmittalItemResponse,
)
from app.graphql.submittals.strawberry.submittal_response import SubmittalResponse
from app.graphql.submittals.strawberry.submittal_returned_pdf_response import (
    SubmittalReturnedPdfResponse,
)
from app.graphql.submittals.strawberry.submittal_revision_response import (
    SubmittalRevisionResponse,
)
from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
    SubmittalStakeholderResponse,
)


@strawberry.type
class SubmittalsMutations:
    @strawberry.mutation
    @inject
    async def create_submittal(
        self,
        service: Injected[SubmittalsService],
        input: CreateSubmittalInput,
    ) -> SubmittalResponse:
        """
        Create a new submittal.

        Args:
            input: Submittal creation data

        Returns:
            Created SubmittalResponse
        """
        submittal = await service.create_submittal(input)
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.mutation
    @inject
    async def update_submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
        input: UpdateSubmittalInput,
    ) -> SubmittalResponse:
        """
        Update an existing submittal.

        Args:
            id: UUID of the submittal to update
            input: Update data

        Returns:
            Updated SubmittalResponse
        """
        submittal = await service.update_submittal(id, input)
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.mutation
    @inject
    async def delete_submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Delete a submittal.

        Args:
            id: UUID of the submittal to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_submittal(id)

    # Item mutations
    @strawberry.mutation
    @inject
    async def add_submittal_item(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalItemInput,
    ) -> SubmittalItemResponse:
        """
        Add an item to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input: Item data

        Returns:
            Created SubmittalItemResponse
        """
        item = await service.add_item(submittal_id, input)
        return SubmittalItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def update_submittal_item(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
        input: UpdateSubmittalItemInput,
    ) -> SubmittalItemResponse:
        """
        Update a submittal item.

        Args:
            id: UUID of the item to update
            input: Update data

        Returns:
            Updated SubmittalItemResponse
        """
        item = await service.update_item(id, input)
        return SubmittalItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def remove_submittal_item(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Remove an item from a submittal.

        Args:
            id: UUID of the item to remove

        Returns:
            True if removed successfully
        """
        return await service.remove_item(id)

    # Stakeholder mutations
    @strawberry.mutation
    @inject
    async def add_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalStakeholderInput,
    ) -> SubmittalStakeholderResponse:
        """
        Add a stakeholder to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input: Stakeholder data

        Returns:
            Created SubmittalStakeholderResponse
        """
        stakeholder = await service.add_stakeholder(submittal_id, input)
        return SubmittalStakeholderResponse.from_orm_model(stakeholder)

    @strawberry.mutation
    @inject
    async def remove_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Remove a stakeholder from a submittal.

        Args:
            id: UUID of the stakeholder to remove

        Returns:
            True if removed successfully
        """
        return await service.remove_stakeholder(id)

    # Revision mutations
    @strawberry.mutation
    @inject
    async def create_submittal_revision(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        notes: str | None = None,
    ) -> SubmittalRevisionResponse:
        """
        Create a new revision for a submittal.

        Args:
            submittal_id: UUID of the submittal
            notes: Optional notes for the revision

        Returns:
            Created SubmittalRevisionResponse
        """
        revision = await service.create_revision(submittal_id, notes)
        return SubmittalRevisionResponse.from_orm_model(revision)

    # Email mutations
    @strawberry.mutation
    @inject
    async def send_submittal_email(
        self,
        service: Injected[SubmittalsService],
        input: SendSubmittalEmailInput,
    ) -> SendSubmittalEmailResponse:
        """
        Send an email for a submittal.

        This mutation:
        1. Sends the email via the user's connected email provider (O365/Gmail)
        2. Records the email in the database for tracking

        Args:
            input: Email data including recipients, subject, and body

        Returns:
            SendSubmittalEmailResponse with success status and email details
        """
        result = await service.send_email(input)
        return SendSubmittalEmailResponse.from_result(result)

    # PDF Generation mutations
    @strawberry.mutation
    @inject
    async def generate_submittal_pdf(
        self,
        service: Injected[SubmittalsService],
        input: GenerateSubmittalPdfInput,
    ) -> GenerateSubmittalPdfResponse:
        """
        Generate a PDF for a submittal.

        This mutation:
        1. Generates a PDF with cover page, transmittal, and items
        2. Optionally includes spec sheet pages
        3. Creates a new revision if requested
        4. Returns a URL to download the PDF

        Args:
            input: PDF generation options including which pages to include

        Returns:
            GenerateSubmittalPdfResponse with PDF URL and revision info
        """
        result = await service.generate_pdf(input)

        if not result.success:
            return GenerateSubmittalPdfResponse.error_response(
                result.error or "Unknown error generating PDF"
            )

        revision_response = None
        if result.revision:
            from app.graphql.submittals.strawberry.submittal_revision_response import (
                SubmittalRevisionResponse,
            )

            revision_response = SubmittalRevisionResponse.from_orm_model(
                result.revision
            )

        return GenerateSubmittalPdfResponse.success_response(
            pdf_url=result.pdf_url or "",
            pdf_file_name=result.pdf_file_name or "submittal.pdf",
            pdf_file_size_bytes=result.pdf_file_size_bytes,
            revision=revision_response,
            email_sent=result.email_sent,
            email_recipients_count=result.email_recipients_count,
        )

    # Returned PDF mutations
    @strawberry.mutation
    @inject
    async def add_returned_pdf(
        self,
        service: Injected[SubmittalsService],
        input: AddReturnedPdfInput,
    ) -> SubmittalReturnedPdfResponse:
        """
        Add a returned PDF to a revision.

        This mutation records a PDF that was returned by a stakeholder
        (engineer, architect, etc.) after reviewing a submittal.

        Args:
            input: Returned PDF data including file info and optional stakeholder

        Returns:
            SubmittalReturnedPdfResponse with the created returned PDF
        """
        returned_pdf = await service.add_returned_pdf(input)
        return SubmittalReturnedPdfResponse.from_orm_model(returned_pdf)

    # Change Analysis mutations
    @strawberry.mutation
    @inject
    async def add_change_analysis(
        self,
        service: Injected[SubmittalsService],
        input: AddChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        """
        Add a change analysis to a returned PDF.

        This mutation records the analysis of changes found in a returned PDF,
        either manually or via AI analysis. It includes the overall status
        and optionally a list of item-level changes.

        Args:
            input: Change analysis data including status and item changes

        Returns:
            SubmittalChangeAnalysisResponse with the created analysis
        """
        change_analysis = await service.add_change_analysis(input)
        return SubmittalChangeAnalysisResponse.from_orm_model(change_analysis)

    # Item Change mutations
    @strawberry.mutation
    @inject
    async def update_item_change(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
        input: UpdateItemChangeInput,
    ) -> SubmittalItemChangeResponse:
        """
        Update an item change in a change analysis.

        This mutation allows updating the status, notes, page references,
        and other fields of an individual item change.

        Args:
            id: UUID of the item change to update
            input: Update data including status, notes, page_references, resolved

        Returns:
            SubmittalItemChangeResponse with the updated item change
        """
        item_change = await service.update_item_change(id, input)
        return SubmittalItemChangeResponse.from_orm_model(item_change)

    @strawberry.mutation
    @inject
    async def delete_item_change(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Delete an item change from a change analysis.

        This mutation removes an item change and updates the parent
        analysis's total_changes_detected count.

        Args:
            id: UUID of the item change to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_item_change(id)

    @strawberry.mutation
    @inject
    async def resolve_item_change(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> SubmittalItemChangeResponse:
        """
        Mark an item change as resolved.

        This is a convenience mutation that sets resolved=True on an item change.
        Used when the user has addressed the change and wants to mark it complete.

        Args:
            id: UUID of the item change to resolve

        Returns:
            SubmittalItemChangeResponse with resolved=True
        """
        item_change = await service.resolve_item_change(id)
        return SubmittalItemChangeResponse.from_orm_model(item_change)
