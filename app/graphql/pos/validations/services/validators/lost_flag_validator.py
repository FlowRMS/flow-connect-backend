from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

TRUTHY_VALUES = {"Y", "YES", "TRUE", "1", "X"}


class LostFlagValidator(BaseValidator):
    validation_key = "lost_flag"
    validation_type = ValidationType.VALIDATION_WARNING

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        lost_flag_value = row.data.get("lost_flag")
        if lost_flag_value is None:
            return []

        str_value = str(lost_flag_value).upper().strip()
        if str_value in TRUTHY_VALUES:
            return [
                ValidationIssue(
                    row_number=row.row_number,
                    column_name="lost_flag",
                    validation_key=self.validation_key,
                    message=f"Lost flag is set: {lost_flag_value}",
                    row_data=row.data,
                )
            ]

        return []
