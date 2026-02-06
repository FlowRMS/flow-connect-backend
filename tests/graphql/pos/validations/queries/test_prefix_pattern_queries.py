import uuid
from unittest.mock import MagicMock

import strawberry

from app.graphql.pos.validations.strawberry.prefix_pattern_types import (
    PrefixPatternResponse,
)


class TestPrefixPatternResponse:
    def test_response_structure(self) -> None:
        """PrefixPatternResponse has correct structure."""
        response = PrefixPatternResponse(
            id=strawberry.ID(str(uuid.uuid4())),
            name="Test Pattern",
            description="Test Description",
            created_at=None,
        )

        assert response.name == "Test Pattern"
        assert response.description == "Test Description"

    def test_from_model_maps_fields(self) -> None:
        """PrefixPatternResponse.from_model maps fields correctly."""
        pattern_id = uuid.uuid4()
        mock_pattern = MagicMock()
        mock_pattern.id = pattern_id
        mock_pattern.name = "My Pattern"
        mock_pattern.description = "My Description"
        mock_pattern.created_at = MagicMock()

        result = PrefixPatternResponse.from_model(mock_pattern)

        assert str(result.id) == str(pattern_id)
        assert result.name == "My Pattern"
        assert result.description == "My Description"

    def test_from_model_handles_none_description(self) -> None:
        """PrefixPatternResponse.from_model handles None description."""
        mock_pattern = MagicMock()
        mock_pattern.id = uuid.uuid4()
        mock_pattern.name = "Pattern Without Description"
        mock_pattern.description = None
        mock_pattern.created_at = None

        result = PrefixPatternResponse.from_model(mock_pattern)

        assert result.description is None
