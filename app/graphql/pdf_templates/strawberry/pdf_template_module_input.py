

from uuid import UUID

import strawberry

from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule


@strawberry.input
class PdfTemplateModuleInput:

    id: str | None = strawberry.UNSET
    module_type: str
    position: int
    config: strawberry.scalars.JSON

    def to_orm_model(self, template_id: UUID | str) -> PdfTemplateModule:
        if isinstance(template_id, str):
            template_id = UUID(template_id)
        
        # Ensure config is a dict
        config_value: dict = {}
        if self.config is not None and self.config != strawberry.UNSET:
            if isinstance(self.config, dict):
                config_value = self.config
            else:
                config_value = {}
        
        return PdfTemplateModule(
            template_id=template_id,
            module_type=self.module_type,
            position=self.position,
            config=config_value,
        )

