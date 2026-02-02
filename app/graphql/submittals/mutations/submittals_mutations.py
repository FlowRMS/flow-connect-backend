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
    UpdateSubmittalInput,
    UpdateSubmittalItemInput,
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
        submittal = await service.update_submittal(id, input)
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.mutation
    @inject
    async def delete_submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        return await service.delete_submittal(id)

    @strawberry.mutation
    @inject
    async def add_submittal_item(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalItemInput,
    ) -> SubmittalItemResponse:
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
        item = await service.update_item(id, input)
        return SubmittalItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def remove_submittal_item(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        return await service.remove_item(id)

    @strawberry.mutation
    @inject
    async def add_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalStakeholderInput,
    ) -> SubmittalStakeholderResponse:
        stakeholder = await service.add_stakeholder(submittal_id, input)
        return SubmittalStakeholderResponse.from_orm_model(stakeholder)

    @strawberry.mutation
    @inject
    async def remove_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        return await service.remove_stakeholder(id)

    @strawberry.mutation
    @inject
    async def create_submittal_revision(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        notes: str | None = None,
    ) -> SubmittalRevisionResponse:
        revision = await service.create_revision(submittal_id, notes)
        return SubmittalRevisionResponse.from_orm_model(revision)

    @strawberry.mutation
    @inject
    async def send_submittal_email(
        self,
        service: Injected[SubmittalsService],
        input: SendSubmittalEmailInput,
    ) -> SendSubmittalEmailResponse:
        result = await service.send_email(input)
        return SendSubmittalEmailResponse.from_result(result)

    @strawberry.mutation
    @inject
    async def generate_submittal_pdf(
        self,
        service: Injected[SubmittalsService],
        input: GenerateSubmittalPdfInput,
    ) -> GenerateSubmittalPdfResponse:
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

    @strawberry.mutation
    @inject
    async def add_returned_pdf(
        self,
        service: Injected[SubmittalsService],
        input: AddReturnedPdfInput,
    ) -> SubmittalReturnedPdfResponse:
        returned_pdf = await service.add_returned_pdf(input)
        return SubmittalReturnedPdfResponse.from_orm_model(returned_pdf)

    @strawberry.mutation
    @inject
    async def add_change_analysis(
        self,
        service: Injected[SubmittalsService],
        input: AddChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        change_analysis = await service.add_change_analysis(input)
        return SubmittalChangeAnalysisResponse.from_orm_model(change_analysis)
