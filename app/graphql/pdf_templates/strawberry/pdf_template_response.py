

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate
from app.graphql.pdf_templates.strawberry.pdf_template_module_response import (
    PdfTemplateModuleResponse,
)
from app.graphql.pdf_templates.strawberry.pdf_template_type_response import (
    PdfTemplateTypeResponse,
)
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class PdfTemplateResponse(DTOMixin[PdfTemplate]):


    _instance: strawberry.Private[PdfTemplate]
    id: str
    name: str
    description: str | None
    template_type_code: str
    template_type_id: UUID | None
    is_default: bool
    is_system: bool
    global_styles: strawberry.scalars.JSON
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: PdfTemplate) -> Self:

        return cls(
            _instance=model,
            id=str(model.id),
            name=model.name,
            description=model.description,
            template_type_code=model.template_type_code,
            template_type_id=model.template_type_id,
            is_default=model.is_default,
            is_system=model.is_system,
            global_styles=model.global_styles or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    def template_type(self) -> PdfTemplateTypeResponse | None:

        if self._instance.template_type is None:
            return None
        return PdfTemplateTypeResponse.from_orm_model(self._instance.template_type)

    @strawberry.field
    def modules(self) -> list[PdfTemplateModuleResponse]:

        return [
            PdfTemplateModuleResponse.from_orm_model(module)
            for module in self._instance.modules
        ]

    @strawberry.field
    def created_by(self) -> UserResponse | None:

        if self._instance.created_by is None:
            return None
        return UserResponse.from_orm_model(self._instance.created_by)

