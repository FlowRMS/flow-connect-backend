import pytest

from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.strawberry.validation_rule_types import (
    ValidationRuleResponse,
)


class TestValidationRuleResponse:
    def test_validations_returns_all_validations(self) -> None:
        """get_all returns complete list of 16 validations."""
        validations = ValidationRuleResponse.get_all()

        assert len(validations) == 16

    def test_validation_has_required_fields(self) -> None:
        """Each validation has name, description, triggers, type, enabled."""
        validations = ValidationRuleResponse.get_all()

        for validation in validations:
            assert isinstance(validation.name, str)
            assert len(validation.name) > 0
            assert isinstance(validation.description, str)
            assert len(validation.description) > 0
            assert isinstance(validation.triggers, list)
            assert isinstance(validation.validation_type, ValidationType)
            assert isinstance(validation.enabled, bool)

    def test_validation_types_are_valid_enum_values(self) -> None:
        """Type field is one of the three valid enum values."""
        validations = ValidationRuleResponse.get_all()
        valid_types = {
            ValidationType.STANDARD_VALIDATION,
            ValidationType.VALIDATION_WARNING,
            ValidationType.AI_POWERED_VALIDATION,
        }

        for validation in validations:
            assert validation.validation_type in valid_types

    def test_standard_validations_count(self) -> None:
        """There are 7 standard validations."""
        validations = ValidationRuleResponse.get_all()
        standard = [
            v
            for v in validations
            if v.validation_type == ValidationType.STANDARD_VALIDATION
        ]

        assert len(standard) == 7

    def test_validation_warnings_count(self) -> None:
        """There are 4 validation warnings."""
        validations = ValidationRuleResponse.get_all()
        warnings = [
            v
            for v in validations
            if v.validation_type == ValidationType.VALIDATION_WARNING
        ]

        assert len(warnings) == 4

    def test_ai_powered_validations_count(self) -> None:
        """There are 5 AI-powered validations."""
        validations = ValidationRuleResponse.get_all()
        ai_powered = [
            v
            for v in validations
            if v.validation_type == ValidationType.AI_POWERED_VALIDATION
        ]

        assert len(ai_powered) == 5

    def test_only_two_validations_have_triggers(self) -> None:
        """Only 2 validations have non-empty triggers list."""
        validations = ValidationRuleResponse.get_all()
        with_triggers = [v for v in validations if len(v.triggers) > 0]

        assert len(with_triggers) == 2

    @pytest.mark.parametrize(
        "validation_name",
        [
            "Line-level transaction data required",
            "Required field validation",
            "Date format validation",
            "Numeric field validation",
            "ZIP code validation",
            "Price calculation check",
            "Future date prevention",
            "Catalog/Part number format check",
            "Lot order detection",
            "Ship-from location comparison",
            "Include lost flag",
            "Duplicate detection",
            "Anomaly detection",
            "Catalog number verification",
            "Address standardization",
            "Historical comparison",
        ],
    )
    def test_validation_names_exist(self, validation_name: str) -> None:
        """All expected validation names are present."""
        validations = ValidationRuleResponse.get_all()
        names = [v.name for v in validations]

        assert validation_name in names
