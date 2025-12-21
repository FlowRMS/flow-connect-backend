

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.pdf_templates.services import (
    PdfTemplateTypesService,
    PdfTemplatesService,
)
from app.graphql.pdf_templates.strawberry.pdf_template_input import PdfTemplateInput
from app.graphql.pdf_templates.strawberry.pdf_template_response import (
    PdfTemplateResponse,
)
from app.graphql.pdf_templates.strawberry.pdf_template_type_input import (
    PdfTemplateTypeInput,
)
from app.graphql.pdf_templates.strawberry.pdf_template_type_response import (
    PdfTemplateTypeResponse,
)


@strawberry.type
class PdfTemplatesMutations:

    @strawberry.mutation
    @inject
    async def create_pdf_template(
        self,
        input: PdfTemplateInput,
        service: Injected[PdfTemplatesService],
    ) -> PdfTemplateResponse:
        return PdfTemplateResponse.from_orm_model(await service.create_template(input))

    @strawberry.mutation
    @inject
    async def update_pdf_template(
        self,
        id: UUID,
        input: PdfTemplateInput,
        service: Injected[PdfTemplatesService],
    ) -> PdfTemplateResponse:
        return PdfTemplateResponse.from_orm_model(
            await service.update_template(id, input)
        )

    @strawberry.mutation
    @inject
    async def delete_pdf_template(
        self,
        id: UUID,
        service: Injected[PdfTemplatesService],
    ) -> bool:
        return await service.delete_template(id)

    @strawberry.mutation
    @inject
    async def copy_pdf_template(
        self,
        id: UUID,
        service: Injected[PdfTemplatesService],
        new_name: str | None = None,
    ) -> PdfTemplateResponse:
        return PdfTemplateResponse.from_orm_model(
            await service.copy_template(id, new_name)
        )

    @strawberry.mutation
    @inject
    async def create_pdf_template_type(
        self,
        input: PdfTemplateTypeInput,
        service: Injected[PdfTemplateTypesService],
    ) -> PdfTemplateTypeResponse:
        return PdfTemplateTypeResponse.from_orm_model(
            await service.create_template_type(input)
        )

    @strawberry.mutation
    @inject
    async def update_pdf_template_type(
        self,
        id: UUID,
        input: PdfTemplateTypeInput,
        service: Injected[PdfTemplateTypesService],
    ) -> PdfTemplateTypeResponse:
        return PdfTemplateTypeResponse.from_orm_model(
            await service.update_template_type(id, input)
        )

    @strawberry.mutation
    @inject
    async def delete_pdf_template_type(
        self,
        id: UUID,
        service: Injected[PdfTemplateTypesService],
    ) -> bool:
        return await service.delete_template_type(id)

