
import logging
from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.pdf_templates.models.pdf_template_type_model import PdfTemplateType
from app.graphql.pdf_templates.repositories.pdf_templates_repository import (
    PdfTemplateTypesRepository,
)
from app.graphql.pdf_templates.strawberry.pdf_template_type_input import (
    PdfTemplateTypeInput,
)

logger = logging.getLogger(__name__)


class PdfTemplateTypesService:

    def __init__(
        self,
        repository: PdfTemplateTypesRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def create_template_type(
        self, template_type_input: PdfTemplateTypeInput
    ) -> PdfTemplateType:

        if template_type_input.display_order is not None:
            if template_type_input.display_order < 1:
                raise ValueError("Display order must be at least 1")
            if await self.repository.exists_with_display_order(
                template_type_input.display_order
            ):
                raise ValueError(
                    f"Display order {template_type_input.display_order} is already in use"
                )

        template_type = template_type_input.to_orm_model()
        return await self.repository.create(template_type)

    async def update_template_type(
        self, template_type_id: UUID, template_type_input: PdfTemplateTypeInput
    ) -> PdfTemplateType:

        if not await self.repository.exists(template_type_id):
            raise NotFoundError(str(template_type_id))

        if template_type_input.display_order is not None:
            if template_type_input.display_order < 1:
                raise ValueError("Display order must be at least 1")
            if await self.repository.exists_with_display_order(
                template_type_input.display_order, exclude_id=template_type_id
            ):
                raise ValueError(
                    f"Display order {template_type_input.display_order} is already in use"
                )

        template_type = template_type_input.to_orm_model()
        template_type.id = template_type_id
        return await self.repository.update(template_type)

    async def delete_template_type(self, template_type_id: UUID) -> bool:

        if not await self.repository.exists(template_type_id):
            raise NotFoundError(str(template_type_id))
        return await self.repository.delete(template_type_id)

    async def get_template_type(self, template_type_id: UUID) -> PdfTemplateType:

        template_type = await self.repository.get_by_id(template_type_id)
        if not template_type:
            raise NotFoundError(str(template_type_id))
        return template_type

    async def get_all_template_types(self, limit: int = 1000) -> list[PdfTemplateType]:

        return await self.repository.get_all_ordered(limit)

