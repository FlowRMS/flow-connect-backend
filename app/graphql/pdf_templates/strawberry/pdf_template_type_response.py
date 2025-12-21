

from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.pdf_templates.models.pdf_template_type_model import PdfTemplateType


@strawberry.type
class PdfTemplateTypeResponse(DTOMixin[PdfTemplateType]):

    _instance: strawberry.Private[PdfTemplateType]
    id: UUID
    name: str
    description: str | None
    display_order: int | None

    @classmethod
    def from_orm_model(cls, model: PdfTemplateType) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            description=model.description,
            display_order=model.display_order,
        )

