from unittest.mock import MagicMock

import httpx
import pytest

from app.core.flow_connect_api.response_handler import raise_for_api_status
from app.errors.common_errors import RemoteApiError


class TestRaiseForApiStatus:
    @pytest.fixture
    def mock_response(self) -> MagicMock:
        return MagicMock(spec=httpx.Response)

    def test_extracts_message_from_500_response(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Returns remote message instead of generic 'Remote API error: 500'."""
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "statusCode": 500,
            "message": "Failed to create organization: duplicate key constraint",
        }

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response)

        assert "Failed to create organization: duplicate key constraint" in str(
            exc_info.value
        )
        assert "Remote API error: 500" not in str(exc_info.value)

    def test_includes_context_in_error_message(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Prefixes error with context when provided."""
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response, context="Creating organization")

        error_message = str(exc_info.value)
        assert error_message.startswith("Creating organization:")

    def test_context_with_extracted_message(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Combines context and remote message correctly."""
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Database connection failed"}

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response, context="Inviting contact")

        error_message = str(exc_info.value)
        assert "Inviting contact:" in error_message
        assert "Database connection failed" in error_message

    def test_context_parameter_is_optional(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Existing calls without context still work."""
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Server error"}

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response)

        assert "Server error" in str(exc_info.value)

    def test_500_without_json_body_uses_generic_message(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Falls back to generic message when response has no valid JSON."""
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("No JSON")

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response)

        assert "500" in str(exc_info.value)

    def test_context_applied_to_400_errors(
        self,
        mock_response: MagicMock,
    ) -> None:
        """Context is also applied to 400 errors."""
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid domain format"}

        with pytest.raises(RemoteApiError) as exc_info:
            raise_for_api_status(mock_response, context="Validating input")

        error_message = str(exc_info.value)
        assert "Validating input:" in error_message
        assert "Invalid domain format" in error_message
