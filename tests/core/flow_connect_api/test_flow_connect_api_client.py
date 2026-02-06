import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.flow_connect_api.flow_connect_api_client import FlowConnectApiClient
from app.core.config.flow_connect_api_settings import FlowConnectApiSettings
from app.errors.common_errors import RemoteApiError


class TestFlowConnectApiClient:
    @pytest.fixture
    def mock_settings(self) -> MagicMock:
        settings = MagicMock(spec=FlowConnectApiSettings)
        settings.flow_connect_api_url = "https://api.example.com"
        return settings

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.access_token = "test-bearer-token"
        return auth_info

    @pytest.fixture
    def client(
        self,
        mock_settings: MagicMock,
        mock_auth_info: MagicMock,
    ) -> FlowConnectApiClient:
        return FlowConnectApiClient(
            settings=mock_settings,
            auth_info=mock_auth_info,
        )

    @pytest.mark.asyncio
    async def test_post_includes_authorization_header(
        self,
        client: FlowConnectApiClient,
    ) -> None:
        """Request includes Bearer token in Authorization header."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            await client.post("/connections/requests", {"target_org_id": str(uuid.uuid4())})

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args.kwargs
            assert call_kwargs["headers"]["Authorization"] == "Bearer test-bearer-token"

    @pytest.mark.asyncio
    async def test_post_sends_json_body(
        self,
        client: FlowConnectApiClient,
    ) -> None:
        """Request body is sent as JSON with correct content."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        target_org_id = str(uuid.uuid4())

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            await client.post("/connections/requests", {"target_org_id": target_org_id})

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args.kwargs
            assert call_kwargs["json"] == {"target_org_id": target_org_id}

    @pytest.mark.asyncio
    async def test_post_returns_response(
        self,
        client: FlowConnectApiClient,
    ) -> None:
        """Returns httpx.Response object from the request."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 201

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await client.post("/connections/requests", {"target_org_id": "123"})

            assert result is mock_response

    @pytest.mark.asyncio
    async def test_post_raises_remote_api_error_on_network_failure(
        self,
        client: FlowConnectApiClient,
    ) -> None:
        """Network errors are wrapped in RemoteApiError."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            with pytest.raises(RemoteApiError) as exc_info:
                await client.post("/connections/requests", {"target_org_id": "123"})

            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_post_constructs_full_url(
        self,
        client: FlowConnectApiClient,
    ) -> None:
        """Combines base URL with endpoint path."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            await client.post("/connections/requests", {"target_org_id": "123"})

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args.kwargs
            assert call_kwargs["url"] == "https://api.example.com/connections/requests"

    @pytest.mark.asyncio
    async def test_post_raises_error_when_url_not_configured(
        self,
        mock_auth_info: MagicMock,
    ) -> None:
        """Raises RemoteApiError when FLOW_CONNECT_API_URL is not configured."""
        settings = MagicMock(spec=FlowConnectApiSettings)
        settings.flow_connect_api_url = None

        client = FlowConnectApiClient(settings=settings, auth_info=mock_auth_info)

        with pytest.raises(RemoteApiError) as exc_info:
            await client.post("/connections/requests", {"target_org_id": "123"})

        assert "FLOW_CONNECT_API_URL is not configured" in str(exc_info.value)
