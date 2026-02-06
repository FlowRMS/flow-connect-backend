from datetime import date, datetime

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import FieldType
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%m-%d-%Y",
    "%d-%m-%Y",
]


class FutureDateValidator(BaseValidator):
    validation_key = "future_date"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        today = date.today()

        for field in field_map.fields:
            if field.field_type_enum != FieldType.DATE:
                continue

            value = row.data.get(field.standard_field_key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue

            parsed_date = self._parse_date(str(value))
            if parsed_date and parsed_date > today:
                issues.append(
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name=field.standard_field_key,
                        validation_key=self.validation_key,
                        message=f"Future date not allowed for '{field.standard_field_key}': {value}",
                        row_data=row.data,
                    )
                )

        return issues

    @staticmethod
    def _parse_date(value: str) -> date | None:
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None
