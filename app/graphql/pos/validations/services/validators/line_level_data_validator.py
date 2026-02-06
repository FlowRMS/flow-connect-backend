from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class LineLevelDataValidator(BaseValidator):
    """
    Validates that data appears to be line-level (individual transactions)
    rather than summary-level data.

    Implementation deferred - complex heuristic validation.
    """

    validation_key = "line_level_data"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        # TODO: Implement heuristic validation
        # - Check for round numbers that suggest aggregation
        # - Look for patterns indicating summary rows
        return []
