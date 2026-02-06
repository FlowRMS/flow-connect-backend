from decimal import Decimal, InvalidOperation

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import FieldType
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class NumericFieldValidator(BaseValidator):
    validation_key = "numeric_field"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for field in field_map.fields:
            if field.field_type_enum not in (FieldType.INTEGER, FieldType.DECIMAL):
                continue

            value = row.data.get(field.standard_field_key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue

            if isinstance(value, (int, float)):
                continue

            str_value = str(value).strip()
            if not self._is_numeric(str_value, field.field_type_enum):
                issues.append(
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name=field.standard_field_key,
                        validation_key=self.validation_key,
                        message=f"Non-numeric value for '{field.standard_field_key}': {value}",
                        row_data=row.data,
                    )
                )

        return issues

    @staticmethod
    def _is_numeric(value: str, field_type: FieldType) -> bool:
        try:
            if field_type == FieldType.INTEGER:
                int(value)
            else:
                Decimal(value)
            return True
        except (ValueError, InvalidOperation):
            return False
