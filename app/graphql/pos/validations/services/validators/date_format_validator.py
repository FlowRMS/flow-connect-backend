from datetime import datetime

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import FieldType
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

DATE_FORMATS = [
    "%Y-%m-%d",  # 2026-01-15
    "%m/%d/%Y",  # 01/15/2026
    "%d/%m/%Y",  # 15/01/2026
    "%Y/%m/%d",  # 2026/01/15
    "%m-%d-%Y",  # 01-15-2026
    "%d-%m-%Y",  # 15-01-2026
]


class DateFormatValidator(BaseValidator):
    validation_key = "date_format"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for field in field_map.fields:
            if field.field_type_enum != FieldType.DATE:
                continue

            value = row.data.get(field.standard_field_key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue

            if not self._is_valid_date(str(value)):
                issues.append(
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name=field.standard_field_key,
                        validation_key=self.validation_key,
                        message=f"Invalid date format for '{field.standard_field_key}': {value}",
                        row_data=row.data,
                    )
                )

        return issues

    @staticmethod
    def _is_valid_date(value: str) -> bool:
        for fmt in DATE_FORMATS:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False
