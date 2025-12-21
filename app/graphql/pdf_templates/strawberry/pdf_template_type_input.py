

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.pdf_templates.models.pdf_template_type_model import PdfTemplateType


@strawberry.input
class PdfTemplateTypeInput(BaseInputGQL[PdfTemplateType]):

    name: str
    description: str | None = strawberry.UNSET
    display_order: int | None = strawberry.UNSET

    def to_orm_model(self) -> PdfTemplateType:
        return PdfTemplateType(
            name=self.name,
            description=self.optional_field(self.description),
            display_order=self.optional_field(self.display_order),
        )

