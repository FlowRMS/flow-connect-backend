

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.pdf_templates.services import (
    PdfTemplateTypesService,
    PdfTemplatesService,
)
from app.graphql.pdf_templates.strawberry.pdf_template_response import (
    PdfTemplateResponse,
)
from app.graphql.pdf_templates.strawberry.pdf_template_type_response import (
    PdfTemplateTypeResponse,
)
from app.graphql.pdf_templates.strawberry.entity_schema_response import (
    EntitySchemasResponse,
)
from app.graphql.pdf_templates.strawberry.entity_data_response import (
    EntityDataResponse,
)


@strawberry.type
class PdfTemplatesQueries:

    @strawberry.field
    @inject
    async def pdf_template(
        self,
        id: UUID,
        service: Injected[PdfTemplatesService],
    ) -> PdfTemplateResponse:
        return PdfTemplateResponse.from_orm_model(await service.get_template(id))

    @strawberry.field
    @inject
    async def pdf_templates(
        self,
        service: Injected[PdfTemplatesService],
        limit: int = 1000,
        template_type_code: str | None = None,
        is_system: bool | None = None,
    ) -> list[PdfTemplateResponse]:
        templates = await service.get_all_templates(limit, template_type_code, is_system)
        return [PdfTemplateResponse.from_orm_model(t) for t in templates]

    @strawberry.field
    @inject
    async def pdf_system_templates(
        self,
        service: Injected[PdfTemplatesService],
        limit: int = 1000,
        template_type_code: str | None = None,
    ) -> list[PdfTemplateResponse]:

        templates = await service.get_system_templates(limit, template_type_code)
        return [PdfTemplateResponse.from_orm_model(t) for t in templates]

    @strawberry.field
    @inject
    async def pdf_templates_by_type_id(
        self,
        template_type_id: UUID,
        service: Injected[PdfTemplatesService],
        limit: int = 1000,
    ) -> list[PdfTemplateResponse]:
        templates = await service.get_templates_by_type_id(template_type_id, limit)
        return [PdfTemplateResponse.from_orm_model(t) for t in templates]

    @strawberry.field
    @inject
    async def pdf_template_default(
        self,
        template_type_code: str,
        service: Injected[PdfTemplatesService],
    ) -> PdfTemplateResponse | None:
        template = await service.get_default_template(template_type_code)
        if template:
            return PdfTemplateResponse.from_orm_model(template)
        return None

    @strawberry.field
    @inject
    async def pdf_template_search(
        self,
        search_term: str,
        service: Injected[PdfTemplatesService],
        limit: int = 20,
    ) -> list[PdfTemplateResponse]:
        templates = await service.search_templates(search_term, limit)
        return [PdfTemplateResponse.from_orm_model(t) for t in templates]

    @strawberry.field
    @inject
    async def pdf_template_types(
        self,
        service: Injected[PdfTemplateTypesService],
        limit: int = 1000,
    ) -> list[PdfTemplateTypeResponse]:
        template_types = await service.get_all_template_types(limit)
        return [PdfTemplateTypeResponse.from_orm_model(tt) for tt in template_types]

    @strawberry.field
    @inject
    async def pdf_template_type(
        self,
        id: UUID,
        service: Injected[PdfTemplateTypesService],
    ) -> PdfTemplateTypeResponse:
        return PdfTemplateTypeResponse.from_orm_model(await service.get_template_type(id))

    @strawberry.field
    @inject
    async def pdf_template_entity_schemas(
        self,
        service: Injected[PdfTemplatesService],
    ) -> EntitySchemasResponse:
        return await service.get_entity_schemas()

    @strawberry.field
    @inject
    async def pdf_template_entity_data(
        self,
        entity_type: str,
        entity_id: UUID,
        service: Injected[PdfTemplatesService],
    ) -> EntityDataResponse:

        data = await service.get_entity_data(entity_type, entity_id)
        return EntityDataResponse(
            entity_type=entity_type,
            entity_id=str(entity_id),
            data=data,
        )

