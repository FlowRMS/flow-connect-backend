import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.errors.common_errors import (
    ConflictError,
    NotFoundError,
    RemoteApiError,
    UnauthorizedError,
)
from app.graphql.connections.services.connection_request_service import (
    ConnectionRequestService,
)


class TestConnectionRequestService:
    @pytest.fixture
    def mock_api_client(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_api_client: AsyncMock) -> ConnectionRequestService:
        return ConnectionRequestService(api_client=mock_api_client)

    @pytest.mark.asyncio
    async def test_create_returns_true_on_201(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Returns True when API responds with 201 Created."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_api_client.post.return_value = mock_response

        result = await service.create_connection_request(uuid.uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_create_returns_true_on_200(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Returns True when API responds with 200 OK."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_api_client.post.return_value = mock_response

        result = await service.create_connection_request(uuid.uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_create_without_draft_sends_draft_false(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Default behavior sends draft: false in payload."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_api_client.post.return_value = mock_response
        target_org_id = uuid.uuid4()

        await service.create_connection_request(target_org_id)

        mock_api_client.post.assert_called_once_with(
            "/connections/requests",
            {"target_org_id": str(target_org_id), "draft": False},
        )

    @pytest.mark.asyncio
    async def test_create_with_draft_true_sends_draft_true(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Explicit draft=True is forwarded in payload."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_api_client.post.return_value = mock_response
        target_org_id = uuid.uuid4()

        await service.create_connection_request(target_org_id, draft=True)

        mock_api_client.post.assert_called_once_with(
            "/connections/requests",
            {"target_org_id": str(target_org_id), "draft": True},
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [401, 403])
    async def test_create_raises_unauthorized_on_401_403(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
        status_code: int,
    ) -> None:
        """Raises UnauthorizedError for 401 and 403 responses."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_api_client.post.return_value = mock_response

        with pytest.raises(UnauthorizedError):
            await service.create_connection_request(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_raises_not_found_on_404(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Raises NotFoundError when target org not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_api_client.post.return_value = mock_response

        with pytest.raises(NotFoundError):
            await service.create_connection_request(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_raises_conflict_on_409(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Raises ConflictError when connection already exists."""
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_api_client.post.return_value = mock_response

        with pytest.raises(ConflictError):
            await service.create_connection_request(uuid.uuid4())

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [500, 502, 503])
    async def test_create_raises_remote_api_error_on_5xx(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
        status_code: int,
    ) -> None:
        """Raises RemoteApiError for server errors."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_api_client.post.return_value = mock_response

        with pytest.raises(RemoteApiError):
            await service.create_connection_request(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_propagates_remote_api_error(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Propagates RemoteApiError from API client (network errors)."""
        mock_api_client.post.side_effect = RemoteApiError("Network error")

        with pytest.raises(RemoteApiError):
            await service.create_connection_request(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_raises_remote_api_error_on_400_with_message(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Raises RemoteApiError with remote message for 400 responses."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "message": "No valid connection type available",
            "error": "Bad Request",
            "statusCode": 400,
        }
        mock_api_client.post.return_value = mock_response

        with pytest.raises(RemoteApiError) as exc_info:
            await service.create_connection_request(uuid.uuid4())

        assert "Remote API: No valid connection type available" in str(exc_info.value)


class TestInviteConnection:
    @pytest.fixture
    def mock_api_client(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_api_client: AsyncMock) -> ConnectionRequestService:
        return ConnectionRequestService(api_client=mock_api_client)

    @pytest.mark.asyncio
    async def test_invite_calls_correct_endpoint(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Calls POST /connections/org/{target_org_id}/invite."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_api_client.post.return_value = mock_response
        target_org_id = uuid.uuid4()

        await service.invite_connection(target_org_id)

        mock_api_client.post.assert_called_once_with(
            f"/connections/org/{target_org_id}/invite",
            {},
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [200, 201])
    async def test_invite_returns_true_on_success(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
        status_code: int,
    ) -> None:
        """Returns True on successful response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_api_client.post.return_value = mock_response

        result = await service.invite_connection(uuid.uuid4())

        assert result is True

    @pytest.mark.asyncio
    async def test_invite_raises_not_found_on_404(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
    ) -> None:
        """Raises NotFoundError when connection not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_api_client.post.return_value = mock_response

        with pytest.raises(NotFoundError):
            await service.invite_connection(uuid.uuid4())

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [401, 403])
    async def test_invite_raises_unauthorized_on_401_403(
        self,
        service: ConnectionRequestService,
        mock_api_client: AsyncMock,
        status_code: int,
    ) -> None:
        """Raises UnauthorizedError for 401 and 403 responses."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_api_client.post.return_value = mock_response

        with pytest.raises(UnauthorizedError):
            await service.invite_connection(uuid.uuid4())
