from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.submittals.services.returned_pdf_service import ReturnedPdfService
from app.graphql.submittals.strawberry.add_item_change_input import AddItemChangeInput
from app.graphql.submittals.strawberry.create_change_analysis_input import (
    CreateChangeAnalysisInput,
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
from app.graphql.submittals.strawberry.update_change_analysis_input import (
    UpdateChangeAnalysisInput,
)
from app.graphql.submittals.strawberry.update_item_change_input import (
    UpdateItemChangeInput,
)
from app.graphql.submittals.strawberry.upload_returned_pdf_input import (
    UploadReturnedPdfInput,
)


@strawberry.type
class ReturnedPdfMutations:
    @strawberry.mutation
    @inject
    async def upload_returned_pdf(
        self,
        service: Injected[ReturnedPdfService],
        input: UploadReturnedPdfInput,
    ) -> SubmittalReturnedPdfResponse:
        returned_pdf = await service.upload_returned_pdf(input)
        return SubmittalReturnedPdfResponse.from_orm_model(returned_pdf)

    @strawberry.mutation
    @inject
    async def delete_returned_pdf(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        return await service.delete_returned_pdf(id)

    @strawberry.mutation
    @inject
    async def create_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        input: CreateChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        analysis = await service.create_change_analysis(input)
        return SubmittalChangeAnalysisResponse.from_orm_model(analysis)

    @strawberry.mutation
    @inject
    async def update_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
        input: UpdateChangeAnalysisInput,
    ) -> SubmittalChangeAnalysisResponse:
        analysis = await service.update_change_analysis(id, input)
        return SubmittalChangeAnalysisResponse.from_orm_model(analysis)

    @strawberry.mutation
    @inject
    async def delete_change_analysis(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        return await service.delete_change_analysis(id)

    @strawberry.mutation
    @inject
    async def add_item_change(
        self,
        service: Injected[ReturnedPdfService],
        input: AddItemChangeInput,
    ) -> SubmittalItemChangeResponse:
        item_change = await service.add_item_change(input)
        return SubmittalItemChangeResponse.from_orm_model(item_change)

    @strawberry.mutation
    @inject
    async def update_item_change(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
        input: UpdateItemChangeInput,
    ) -> SubmittalItemChangeResponse:
        item_change = await service.update_item_change(id, input)
        return SubmittalItemChangeResponse.from_orm_model(item_change)

    @strawberry.mutation
    @inject
    async def delete_item_change(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> bool:
        return await service.delete_item_change(id)

    @strawberry.mutation
    @inject
    async def resolve_item_change(
        self,
        service: Injected[ReturnedPdfService],
        id: UUID,
    ) -> SubmittalItemChangeResponse:
        item_change = await service.resolve_item_change(id)
        return SubmittalItemChangeResponse.from_orm_model(item_change)
