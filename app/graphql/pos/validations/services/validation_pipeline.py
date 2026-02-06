from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class ValidationPipeline:
    def __init__(
        self,
        blocking_validators: list[BaseValidator],
        warning_validators: list[BaseValidator],
    ) -> None:
        self.blocking_validators = blocking_validators
        self.warning_validators = warning_validators

    def validate_row(
        self,
        row: FileRow,
        field_map: FieldMap,
    ) -> list[ValidationIssue]:
        all_issues: list[ValidationIssue] = []

        for validator in self.blocking_validators:
            issues = validator.validate(row, field_map)
            all_issues.extend(issues)

        if all_issues:
            return all_issues

        for validator in self.warning_validators:
            issues = validator.validate(row, field_map)
            all_issues.extend(issues)

        return all_issues

    def validate_rows(
        self,
        rows: list[FileRow],
        field_map: FieldMap,
    ) -> list[ValidationIssue]:
        all_issues: list[ValidationIssue] = []
        for row in rows:
            issues = self.validate_row(row, field_map)
            all_issues.extend(issues)
        return all_issues
