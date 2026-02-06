from app.graphql.pos.validations.strawberry.prefix_pattern_inputs import (
    CreatePrefixPatternInput,
)


class TestCreatePrefixPatternInput:
    def test_input_structure(self) -> None:
        """CreatePrefixPatternInput has correct structure."""
        input_data = CreatePrefixPatternInput(
            name="Test Pattern",
            description="Test Description",
        )

        assert input_data.name == "Test Pattern"
        assert input_data.description == "Test Description"

    def test_input_optional_description(self) -> None:
        """CreatePrefixPatternInput allows optional description."""
        input_data = CreatePrefixPatternInput(name="Pattern Only")

        assert input_data.name == "Pattern Only"
        assert input_data.description is None
