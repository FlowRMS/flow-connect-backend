
import logging
from typing import Any
from uuid import UUID

import strawberry
from commons.auth import AuthInfo

from app.core.strawberry.inputs import BaseInputGQL
from app.errors.common_errors import NotFoundError
from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate
from app.graphql.pdf_templates.repositories.pdf_templates_repository import (
    PdfTemplatesRepository,
)
from app.graphql.pdf_templates.services.pdf_template_types_service import (
    PdfTemplateTypesService,
)
from app.graphql.pdf_templates.strawberry.pdf_template_input import PdfTemplateInput
from app.graphql.pdf_templates.strawberry.pdf_template_module_input import (
    PdfTemplateModuleInput,
)
from app.graphql.pdf_templates.services.entity_schemas_data import (
    build_entity_schemas,
)
from app.graphql.pdf_templates.strawberry.entity_schema_response import (
    EntitySchemasResponse,
)
from app.graphql.pdf_templates.services.entity_data_service import (
    EntityDataService,
)

logger = logging.getLogger(__name__)


class PdfTemplatesService:

    def __init__(
        self,
        repository: PdfTemplatesRepository,
        template_types_service: PdfTemplateTypesService,
        entity_data_service: EntityDataService,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.template_types_service = template_types_service
        self.entity_data_service = entity_data_service
        self.auth_info = auth_info

    async def create_template(self, template_input: PdfTemplateInput) -> PdfTemplate:
        template_type_id = BaseInputGQL.optional_field(template_input.template_type_id)
        if template_type_id is not None:
            try:
                await self.template_types_service.get_template_type(template_type_id)
            except NotFoundError:
                logger.warning(
                    f"Template type {template_type_id} does not exist. "
                    f"Setting template_type_id to None for new template"
                )
                template_type_id = None

        template = template_input.to_orm_model()
        
        template.template_type_id = template_type_id

        if template.is_default:
            await self._unset_other_defaults(template.template_type_code)

        created_template = await self.repository.create(template)

        if template_input.modules != strawberry.UNSET:
            modules = [
                module_input.to_orm_model(str(created_template.id))
                for module_input in template_input.modules
            ]
            for module in modules:
                await self.repository.create_module(module)

        return await self.repository.get_by_id_with_modules(str(created_template.id))

    async def update_template(
        self, template_id: str | UUID, template_input: PdfTemplateInput
    ) -> PdfTemplate:
        if not await self.repository.exists(template_id):
            raise NotFoundError(str(template_id))

        existing_template = await self.repository.get_by_id_with_modules(template_id)
        if not existing_template:
            raise NotFoundError(str(template_id))

        template_type_id = BaseInputGQL.optional_field(template_input.template_type_id)
        if template_type_id is not None:
            try:
                await self.template_types_service.get_template_type(template_type_id)
            except NotFoundError:
                logger.warning(
                    f"Template type {template_type_id} does not exist. "
                    f"Setting template_type_id to None for template {template_id}"
                )
                template_type_id = None

        template = template_input.to_orm_model()
        template.id = str(template_id)
        
        template.template_type_id = template_type_id
        
        template.is_system = existing_template.is_system

        if template.is_default:
            await self._unset_other_defaults(template.template_type_code, exclude_id=str(template_id))

        updated_template = await self.repository.update(template)

        if template_input.modules != strawberry.UNSET:
            await self.repository.delete_modules_by_template_id(str(template_id))

            modules = [
                module_input.to_orm_model(str(template_id))
                for module_input in template_input.modules
            ]
            for module in modules:
                await self.repository.create_module(module)

        return await self.repository.get_by_id_with_modules(str(template_id))

    async def delete_template(self, template_id: str | UUID) -> bool:
        template = await self.repository.get_by_id_with_modules(template_id)
        if not template:
            raise NotFoundError(str(template_id))

        if template.is_system:
            raise ValueError("System templates cannot be deleted")

        return await self.repository.delete(template_id)

    async def get_template(self, template_id: str | UUID) -> PdfTemplate:
        template = await self.repository.get_by_id_with_modules(template_id)
        if not template:
            raise NotFoundError(str(template_id))
        return template

    async def get_all_templates(
        self, limit: int = 1000, template_type_code: str | None = None,
        is_system: bool | None = None
    ) -> list[PdfTemplate]:
        return await self.repository.get_all_with_modules(
            limit, template_type_code, is_system
        )

    async def get_system_templates(
        self, limit: int = 1000, template_type_code: str | None = None
    ) -> list[PdfTemplate]:
        """Get all system templates, optionally filtered by type."""
        return await self.repository.get_system_templates(limit, template_type_code)

    async def get_templates_by_type_id(
        self, template_type_id: UUID, limit: int = 1000
    ) -> list[PdfTemplate]:
        return await self.repository.get_by_template_type_id(template_type_id, limit)

    async def get_default_template(self, template_type_code: str) -> PdfTemplate | None:
        return await self.repository.get_default_template(template_type_code)

    async def search_templates(
        self, search_term: str, limit: int = 20
    ) -> list[PdfTemplate]:
        return await self.repository.search_by_name(search_term, limit)

    async def copy_template(
        self, template_id: str | UUID, new_name: str | None = None
    ) -> PdfTemplate:

        source_template = await self.repository.get_by_id_with_modules(template_id)
        if not source_template:
            raise NotFoundError(str(template_id))
        
        copy_name = new_name or f"{source_template.name} (Copy)"
        
        new_template = PdfTemplate(
            name=copy_name,
            description=source_template.description,
            template_type_code=source_template.template_type_code,
            template_type_id=source_template.template_type_id,
            is_default=False,
            is_system=False,
            global_styles=source_template.global_styles.copy() if source_template.global_styles else {},
        )
        
        created_template = await self.repository.create(new_template)
        
        for module in source_template.modules:
            from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule
            new_module = PdfTemplateModule(
                template_id=str(created_template.id),
                module_type=module.module_type,
                position=module.position,
                config=module.config.copy() if module.config else {},
            )
            await self.repository.create_module(new_module)
        
        return await self.repository.get_by_id_with_modules(str(created_template.id))

    async def _unset_other_defaults(
        self, template_type_code: str, exclude_id: str | None = None
    ) -> None:

        await self.repository.unset_defaults_for_type(template_type_code, exclude_id)


    async def get_entity_schemas(self) -> EntitySchemasResponse:
        entities = build_entity_schemas()
        return EntitySchemasResponse(entities=entities)

    async def get_entity_data(
        self, entity_type: str, entity_id: UUID
    ) -> dict[str, Any]:
        return await self.entity_data_service.get_entity_data(entity_type, entity_id)

