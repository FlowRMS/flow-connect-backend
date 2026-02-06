import uuid
from unittest.mock import MagicMock

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validation_pipeline import ValidationPipeline
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class MockBlockingValidator(BaseValidator):
    validation_key = "mock_blocking"
    validation_type = ValidationType.STANDARD_VALIDATION

    def __init__(self, issues: list[ValidationIssue] | None = None) -> None:
        self.issues = issues or []
        self.called = False

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        self.called = True
        return self.issues


class MockWarningValidator(BaseValidator):
    validation_key = "mock_warning"
    validation_type = ValidationType.VALIDATION_WARNING

    def __init__(self, issues: list[ValidationIssue] | None = None) -> None:
        self.issues = issues or []
        self.called = False

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        self.called = True
        return self.issues


def create_field_map() -> MagicMock:
    field_map = MagicMock(spec=FieldMap)
    field_map.id = uuid.uuid4()
    field_map.fields = []
    return field_map


class TestValidationPipeline:
    def test_pipeline_runs_all_validators(self) -> None:
        """All validators execute when no blocking errors."""
        blocking_validator = MockBlockingValidator()
        warning_validator = MockWarningValidator()

        pipeline = ValidationPipeline(
            blocking_validators=[blocking_validator],
            warning_validators=[warning_validator],
        )

        row = FileRow(row_number=2, data={"field": "value"})
        field_map = create_field_map()

        pipeline.validate_row(row, field_map)

        assert blocking_validator.called
        assert warning_validator.called

    def test_pipeline_stops_on_blocking_errors(self) -> None:
        """If standard validation fails, warnings skip."""
        blocking_issue = ValidationIssue(
            row_number=2,
            column_name="field",
            validation_key="mock_blocking",
            message="Error",
        )
        blocking_validator = MockBlockingValidator(issues=[blocking_issue])
        warning_validator = MockWarningValidator()

        pipeline = ValidationPipeline(
            blocking_validators=[blocking_validator],
            warning_validators=[warning_validator],
        )

        row = FileRow(row_number=2, data={"field": "value"})
        field_map = create_field_map()

        issues = pipeline.validate_row(row, field_map)

        assert blocking_validator.called
        assert not warning_validator.called
        assert len(issues) == 1

    def test_pipeline_continues_with_warnings_only(self) -> None:
        """No blocking errors, warnings run."""
        blocking_validator = MockBlockingValidator()
        warning_issue = ValidationIssue(
            row_number=2,
            column_name="field",
            validation_key="mock_warning",
            message="Warning",
        )
        warning_validator = MockWarningValidator(issues=[warning_issue])

        pipeline = ValidationPipeline(
            blocking_validators=[blocking_validator],
            warning_validators=[warning_validator],
        )

        row = FileRow(row_number=2, data={"field": "value"})
        field_map = create_field_map()

        issues = pipeline.validate_row(row, field_map)

        assert blocking_validator.called
        assert warning_validator.called
        assert len(issues) == 1
        assert issues[0].validation_key == "mock_warning"

    def test_pipeline_collects_all_issues(self) -> None:
        """Issues from all validators collected."""
        blocking_validator1 = MockBlockingValidator()
        blocking_validator2 = MockBlockingValidator()
        warning_issue1 = ValidationIssue(
            row_number=2,
            column_name="field1",
            validation_key="warning1",
            message="Warning 1",
        )
        warning_issue2 = ValidationIssue(
            row_number=2,
            column_name="field2",
            validation_key="warning2",
            message="Warning 2",
        )
        warning_validator1 = MockWarningValidator(issues=[warning_issue1])
        warning_validator2 = MockWarningValidator(issues=[warning_issue2])

        pipeline = ValidationPipeline(
            blocking_validators=[blocking_validator1, blocking_validator2],
            warning_validators=[warning_validator1, warning_validator2],
        )

        row = FileRow(row_number=2, data={"field": "value"})
        field_map = create_field_map()

        issues = pipeline.validate_row(row, field_map)

        assert len(issues) == 2
