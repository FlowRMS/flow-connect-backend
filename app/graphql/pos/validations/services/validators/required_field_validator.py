from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import FieldStatus
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class RequiredFieldValidator(BaseValidator):
    validation_key = "required_field"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for field in field_map.fields:
            if field.status_enum != FieldStatus.REQUIRED:
                continue

            value = row.data.get(field.standard_field_key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                issues.append(
                    ValidationIssue(
                        row_number=row.row_number,
                        column_name=field.standard_field_key,
                        validation_key=self.validation_key,
                        message=f"Required field '{field.standard_field_key}' is missing",
                        row_data=row.data,
                    )
                )

        return issues
