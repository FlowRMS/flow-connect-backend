

from typing import Self

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule


@strawberry.type
class PdfTemplateModuleResponse(DTOMixin[PdfTemplateModule]):

    _instance: strawberry.Private[PdfTemplateModule]
    id: str
    template_id: str
    module_type: str
    position: int
    config: strawberry.scalars.JSON

    @classmethod
    def from_orm_model(cls, model: PdfTemplateModule) -> Self:
        return cls(
            _instance=model,
            id=str(model.id),
            template_id=str(model.template_id),
            module_type=model.module_type,
            position=model.position,
            config=model.config or {},
        )

