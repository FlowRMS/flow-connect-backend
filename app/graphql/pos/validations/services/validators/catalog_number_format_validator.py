from typing import Any

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class CatalogNumberFormatValidator(BaseValidator):
    validation_key = "catalog_number_format"
    validation_type = ValidationType.VALIDATION_WARNING

    def validate(
        self,
        row: FileRow,
        field_map: FieldMap,
        **kwargs: Any,
    ) -> list[ValidationIssue]:
        prefix_patterns: list[str] = kwargs.get("prefix_patterns", [])
        if not prefix_patterns:
            return []

        catalog_value = row.data.get("manufacturer_catalog_number")
        if catalog_value is None:
            return []

        str_value = str(catalog_value)
        for prefix in prefix_patterns:
            if str_value.startswith(prefix):
                return [
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name="manufacturer_catalog_number",
                        validation_key=self.validation_key,
                        message=f"Catalog number has prefix '{prefix}': {catalog_value}",
                        row_data=row.data,
                    )
                ]

        return []
