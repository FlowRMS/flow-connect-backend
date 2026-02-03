from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.submittals import (
    ChangeAnalysisSource,
    ItemChangeStatus,
    OverallChangeStatus,
)

from app.graphql.inject import inject
from app.graphql.submittals.services.returned_pdf_service import (
    AddItemChangeInput as ServiceAddItemChangeInput,
)
from app.graphql.submittals.services.returned_pdf_service import (
    CreateChangeAnalysisInput as ServiceCreateChangeAnalysisInput,
)
from app.graphql.submittals.services.returned_pdf_service import (
    ReturnedPdfService,
)
from app.graphql.submittals.services.returned_pdf_service import (
    UpdateItemChangeInput as ServiceUpdateItemChangeInput,
)
from app.graphql.submittals.services.returned_pdf_service import (
    UploadReturnedPdfInput as ServiceUploadReturnedPdfInput,
)
from app.graphql.submittals.strawberry.returned_pdf_input import (
    AddItemChangeInput,
    CreateChangeAnalysisInput,
    UpdateChangeAnalysisInput,
    UpdateItemChangeInput,
    UploadReturnedPdfInput,
)
from app.graphql.submittals.strawberry.submittal_change_analysis_response import (
    SubmittalChangeAnalysisResponse,
)
from app.graphql.submittals.strawberry.submittal_item_change_response import (
    SubmittalItemChangeResponse,
)
from app.graphql.submittals.strawberry.submittal_returned_pdf_response import (
    SubmittalReturnedPdfResponse,
)


@strawberry.type
class ReturnedPdfMutations:
    """GraphQL mutations for returned PDFs and change analysis."""

    # Returned PDF mutations
    @strawberry.mutation
    @inject
    async def upload_returned_pdf(
        self,
        service: Injected[ReturnedPdfService],
        input: UploadReturnedPdfInput,
    ) -> SubmittalReturnedPdfResponse:
        """
        Upload a returned PDF to a revision.

        This is used when an engineer/architect returns a marked-up PDF
        after reviewing a submittal.

        Args:
            input: Upload data including file info and optional stakeholder

        Returns:
            Created SubmittalReturnedPdfResponse
        """
        service_input = ServiceUploadReturnedPdfInput(
            revision_id=input.revision_id,
            file_name=input.file_name,
            file_url=input.file_url,
            file_size=input.file_size,
            file_id=input.file_id,
            returned_by_stakeholder_id=input.returned_by_stakeholder_id,
            received_date=input.received_date,
            notes=input.notes,
        )
        returned_pdf = await service.upload_returned_pdf(service_input)
        return SubmittalReturnedPdfResponse.from_orm_model(returned_pdf)

    @strawberry.mutation
    @inject
    async def delete_returned_pdf(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        """
        Delete a returned PDF.

        Args:
            id: UUID of the returned PDF to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_returned_pdf(id)

    # Change Analysis mutations
    @strawberry.mutation
    @inject
    async def create_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        input: CreateChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        """
        Create a change analysis for a returned PDF.

        This can be created manually or by AI. Each returned PDF
        can have at most one change analysis.

        Args:
            input: Analysis data including source and overall status

        Returns:
            Created SubmittalChangeAnalysisResponse
        """
        service_input = ServiceCreateChangeAnalysisInput(
            returned_pdf_id=input.returned_pdf_id,
            analyzed_by=ChangeAnalysisSource(input.analyzed_by.value),
            overall_status=OverallChangeStatus(input.overall_status.value),
            summary=input.summary,
        )
        analysis = await service.create_change_analysis(service_input)
        return SubmittalChangeAnalysisResponse.from_orm_model(analysis)

    @strawberry.mutation
    @inject
    async def update_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
        input: UpdateChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        """
        Update a change analysis.

        Args:
            id: UUID of the analysis to update
            input: Update data

        Returns:
            Updated SubmittalChangeAnalysisResponse
        """
        overall_status = None
        if input.overall_status is not None:
            overall_status = OverallChangeStatus(input.overall_status.value)

        analysis = await service.update_change_analysis(
            analysis_id=id,
            overall_status=overall_status,
            summary=input.summary,
        )
        return SubmittalChangeAnalysisResponse.from_orm_model(analysis)

    @strawberry.mutation
    @inject
    async def delete_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        """
        Delete a change analysis.

        Args:
            id: UUID of the analysis to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_change_analysis(id)

    # Item Change mutations
    @strawberry.mutation
    @inject
    async def add_item_change(
        self,
        service: Injected[ReturnedPdfService],
        input: AddItemChangeInput,
    ) -> SubmittalItemChangeResponse:
        """
        Add an item change to a change analysis.

        Each item change records how a specific item was marked
        by the reviewer (approved, approved as noted, revise, rejected).

        Args:
            input: Item change data

        Returns:
            Created SubmittalItemChangeResponse
        """
        service_input = ServiceAddItemChangeInput(
            change_analysis_id=input.change_analysis_id,
            fixture_type=input.fixture_type,
            catalog_number=input.catalog_number,
            manufacturer=input.manufacturer,
            item_id=input.item_id,
            status=ItemChangeStatus(input.status.value),
            notes=input.notes,
            page_references=input.page_references,
        )
        item_change = await service.add_item_change(service_input)
        return SubmittalItemChangeResponse.from_orm_model(item_change)

    @strawberry.mutation
    @inject
    async def update_item_change(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
        input: UpdateItemChangeInput,
    ) -> SubmittalItemChangeResponse:
        """
        Update an item change.

        Args:
            id: UUID of the item change to update
            input: Update data

        Returns:
            Updated SubmittalItemChangeResponse
        """
        status = None
        if input.status is not None:
            status = ItemChangeStatus(input.status.value)

        service_input = ServiceUpdateItemChangeInput(
            status=status,
            notes=input.notes,
            page_references=input.page_references,
            resolved=input.resolved,
        )
        item_change = await service.update_item_change(id, service_input)
        return SubmittalItemChangeResponse.from_orm_model(item_change)

    @strawberry.mutation
    @inject
    async def delete_item_change(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        """
        Delete an item change.

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
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> SubmittalItemChangeResponse:
        """
        Mark an item change as resolved.

        This is used when an issue identified by the reviewer
        has been addressed and is ready for resubmission.

        Args:
            id: UUID of the item change to resolve

        Returns:
            Updated SubmittalItemChangeResponse
        """
        item_change = await service.resolve_item_change(id)
        return SubmittalItemChangeResponse.from_orm_model(item_change)
