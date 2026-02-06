from typing import Any

import httpx
from commons.auth.auth_info import AuthInfo

from app.core.config.flow_connect_api_settings import FlowConnectApiSettings
from app.errors.common_errors import RemoteApiError


class FlowConnectApiClient:
    def __init__(
        self,
        settings: FlowConnectApiSettings,
        auth_info: AuthInfo,
    ) -> None:
        self.settings = settings
        self.auth_info = auth_info

    async def post(self, endpoint: str, body: dict[str, Any]) -> httpx.Response:
        if not self.settings.flow_connect_api_url:
            raise RemoteApiError("FLOW_CONNECT_API_URL is not configured")

        url = f"{self.settings.flow_connect_api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth_info.access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                return await client.post(url=url, json=body, headers=headers)
        except httpx.RequestError as e:
            raise RemoteApiError(str(e)) from e
