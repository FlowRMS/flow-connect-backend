import re

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

ZIP_CODE_FIELDS = {
    "selling_branch_zip_code",
    "shipping_branch_zip_code",
    "bill_to_branch_zip_code",
}

ZIP_PATTERN_5 = re.compile(r"^\d{5}$")
ZIP_PATTERN_9 = re.compile(r"^\d{5}-\d{4}$")


class ZipCodeValidator(BaseValidator):
    validation_key = "zip_code"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for field in field_map.fields:
            if field.standard_field_key not in ZIP_CODE_FIELDS:
                continue

            value = row.data.get(field.standard_field_key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue

            str_value = str(value).strip()
            if not self._is_valid_zip(str_value):
                issues.append(
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name=field.standard_field_key,
                        validation_key=self.validation_key,
                        message=f"Invalid ZIP code format for '{field.standard_field_key}': {value}",
                        row_data=row.data,
                    )
                )

        return issues

    @staticmethod
    def _is_valid_zip(value: str) -> bool:
        return bool(ZIP_PATTERN_5.match(value) or ZIP_PATTERN_9.match(value))
