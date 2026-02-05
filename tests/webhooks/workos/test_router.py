import hashlib
import hmac
import json
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aioinject
import pytest
from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from app.core.config.workos_settings import WorkOSSettings
from app.webhooks.workos.services.user_sync_service import UserSyncService


@pytest.fixture
def webhook_secret() -> str:
    return "test_webhook_secret_12345"


@pytest.fixture
def user_created_payload() -> dict[str, Any]:
    return {
        "id": "event_01234567890",
        "event": "user.created",
        "created_at": "2026-01-30T12:00:00.000Z",
        "data": {
            "id": "user_01ABCDEFGHIJKLMNOP",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "email_verified": True,
            "external_id": None,
            "created_at": "2026-01-30T12:00:00.000Z",
            "updated_at": "2026-01-30T12:00:00.000Z",
        },
    }


def generate_signature(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    if timestamp is None:
        timestamp = int(time.time() * 1000)
    message = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp}, v1={signature}"


def create_test_app(service_mock: AsyncMock, webhook_secret: str) -> FastAPI:
    from app.webhooks.workos.router import router

    mock_settings = MagicMock(spec=WorkOSSettings)
    mock_settings.workos_webhook_secret = webhook_secret

    container = aioinject.Container()
    container.register(aioinject.Object(service_mock, interface=UserSyncService))
    container.register(aioinject.Object(mock_settings, interface=WorkOSSettings))

    app = FastAPI()
    app.add_middleware(AioInjectMiddleware, container=container)
    app.include_router(router)
    return app


def post_webhook(
    service_mock: AsyncMock,
    payload: dict[str, Any],
    webhook_secret: str,
    signature: str | None = None,
) -> Response:
    payload_bytes = json.dumps(payload).encode()
    if signature is None:
        signature = generate_signature(payload_bytes, webhook_secret)

    app = create_test_app(service_mock, webhook_secret)

    with TestClient(app) as client:
        response = client.post(
            "/",
            content=payload_bytes,
            headers={
                "Content-Type": "application/json",
                "WorkOS-Signature": signature,
            },
        )
        return response


class TestWebhookSignatureValidation:

    @pytest.mark.asyncio
    async def test_webhook_rejects_missing_signature(
        self, webhook_secret: str
    ) -> None:
        service_mock = AsyncMock()
        app = create_test_app(service_mock, webhook_secret)
        with TestClient(app) as client:
            response = client.post("/", json={"event": "user.created", "data": {}})

        assert response.status_code == 401
        assert "signature" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_webhook_rejects_invalid_signature(
        self,
        webhook_secret: str,
        user_created_payload: dict[str, Any],
    ) -> None:
        service_mock = AsyncMock()
        response = post_webhook(
            service_mock,
            user_created_payload,
            webhook_secret,
            signature="t=123, v1=invalid_signature",
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_webhook_accepts_valid_signature(
        self,
        webhook_secret: str,
        user_created_payload: dict[str, Any],
    ) -> None:
        service_mock = AsyncMock()
        response = post_webhook(service_mock, user_created_payload, webhook_secret)
        assert response.status_code == 200


class TestWebhookEventParsing:

    @pytest.mark.asyncio
    async def test_webhook_parses_user_created_event(
        self,
        webhook_secret: str,
        user_created_payload: dict[str, Any],
    ) -> None:
        service_mock = AsyncMock()
        response = post_webhook(service_mock, user_created_payload, webhook_secret)
        assert response.status_code == 200
        service_mock.handle_user_created.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_ignores_non_user_created_events(
        self,
        webhook_secret: str,
    ) -> None:
        payload = {
            "id": "event_01234567890",
            "event": "user.updated",
            "created_at": "2026-01-30T12:00:00.000Z",
            "data": {"id": "user_01ABCDEFGHIJKLMNOP"},
        }
        service_mock = AsyncMock()
        response = post_webhook(service_mock, payload, webhook_secret)
        assert response.status_code == 200
        service_mock.handle_user_created.assert_not_called()
