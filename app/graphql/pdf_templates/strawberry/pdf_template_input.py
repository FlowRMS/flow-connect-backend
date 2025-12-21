
from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate
from app.graphql.pdf_templates.strawberry.pdf_template_module_input import (
    PdfTemplateModuleInput,
)


@strawberry.input
class PdfTemplateInput(BaseInputGQL[PdfTemplate]):

    name: str
    description: str | None = strawberry.UNSET
    template_type_code: str
    template_type_id: UUID | None = strawberry.UNSET
    is_default: bool = False
    is_system: bool = False
    global_styles: strawberry.scalars.JSON = strawberry.UNSET
    modules: list[PdfTemplateModuleInput] = strawberry.UNSET

    def to_orm_model(self) -> PdfTemplate:
        import json
        
        global_styles_value = self.optional_field(self.global_styles, {})
        
        if isinstance(global_styles_value, str):
            try:
                if global_styles_value.startswith('{') or global_styles_value.startswith('['):
                    global_styles_value = json.loads(global_styles_value)
                else:
                    global_styles_value = {}
            except (json.JSONDecodeError, TypeError, ValueError):
                global_styles_value = {}
        
        if not isinstance(global_styles_value, dict):
            global_styles_value = {}
        
        if global_styles_value and isinstance(global_styles_value, dict):
            cleaned_dict = {}
            for key, value in global_styles_value.items():
                if not (isinstance(key, str) and key.isdigit()):
                    cleaned_dict[key] = value
            global_styles_value = cleaned_dict

        try:
            serialized = json.dumps(global_styles_value)
            if len(serialized) > 1_000_000:  
                global_styles_value = {}
        except (TypeError, ValueError):
            global_styles_value = {}
        
        return PdfTemplate(
            name=self.name,
            description=self.optional_field(self.description),
            template_type_code=self.template_type_code,
            template_type_id=self.optional_field(self.template_type_id),
            is_default=self.is_default,
            is_system=self.is_system,
            global_styles=global_styles_value,
        )

