import time
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.webhooks.workos.router import create_workos_webhook_router
from tests.webhooks.workos.conftest import generate_workos_signature


class TestWorkOSWebhookRouter:
    @pytest.fixture
    def webhook_secret(self) -> str:
        return "whsec_test_secret_key_12345"

    @pytest.fixture
    def mock_provisioning_service(self) -> AsyncMock:
        mock: Any = AsyncMock()
        return mock

    @pytest.fixture
    def app(
        self,
        webhook_secret: str,
        mock_provisioning_service: AsyncMock,
    ) -> FastAPI:
        app = FastAPI()
        router = create_workos_webhook_router(
            webhook_secret,
            provisioning_service=mock_provisioning_service,
        )
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def organization_created_payload(self) -> dict:
        return {
            "id": "event_01ABC123",
            "event": "organization.created",
            "created_at": "2026-01-27T14:00:00Z",
            "data": {
                "id": "org_01XYZ789",
                "name": "Acme Corp",
                "object": "organization",
                "external_id": "ext-123",
                "domains": [],
                "created_at": "2026-01-27T14:00:00Z",
                "updated_at": "2026-01-27T14:00:00Z",
            },
        }

    def test_webhook_valid_signature_returns_200(
        self,
        client: TestClient,
        webhook_secret: str,
        organization_created_payload: dict,
    ) -> None:
        """Valid request with correct signature returns 200."""
        signature, payload_bytes = generate_workos_signature(
            organization_created_payload,
            webhook_secret,
        )

        with patch(
            "app.webhooks.workos.router.handle_organization_created",
            new_callable=AsyncMock,
        ):
            response = client.post(
                "/webhooks/workos",
                content=payload_bytes,
                headers={
                    "WorkOS-Signature": signature,
                    "Content-Type": "application/json",
                },
            )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_webhook_missing_signature_returns_401(
        self,
        client: TestClient,
        organization_created_payload: dict,
    ) -> None:
        """Request without signature header returns 401."""
        response = client.post(
            "/webhooks/workos",
            json=organization_created_payload,
        )

        assert response.status_code == 401

    def test_webhook_invalid_signature_returns_401(
        self,
        client: TestClient,
        organization_created_payload: dict,
    ) -> None:
        """Invalid signature returns 401."""
        timestamp = int(time.time() * 1000)
        invalid_signature = f"t={timestamp}, v1=invalid_signature_hash"

        response = client.post(
            "/webhooks/workos",
            json=organization_created_payload,
            headers={"WorkOS-Signature": invalid_signature},
        )

        assert response.status_code == 401

    def test_webhook_expired_signature_returns_401(
        self,
        client: TestClient,
        webhook_secret: str,
        organization_created_payload: dict,
    ) -> None:
        """Expired signature (>5 min old) returns 401."""
        old_timestamp = int((time.time() - 600) * 1000)  # 10 minutes ago
        signature, payload_bytes = generate_workos_signature(
            organization_created_payload,
            webhook_secret,
            timestamp=old_timestamp,
        )

        response = client.post(
            "/webhooks/workos",
            content=payload_bytes,
            headers={
                "WorkOS-Signature": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 401

    def test_webhook_unknown_event_returns_200(
        self,
        client: TestClient,
        webhook_secret: str,
    ) -> None:
        """Unknown event types are acknowledged but not processed."""
        payload = {
            "id": "event_01ABC123",
            "event": "user.created",
            "created_at": "2026-01-27T14:00:00Z",
            "data": {
                "id": "user_01XYZ789",
                "name": "John Doe",
                "object": "user",
                "external_id": None,
                "domains": [],
                "created_at": "2026-01-27T14:00:00Z",
                "updated_at": "2026-01-27T14:00:00Z",
            },
        }
        signature, payload_bytes = generate_workos_signature(payload, webhook_secret)

        response = client.post(
            "/webhooks/workos",
            content=payload_bytes,
            headers={
                "WorkOS-Signature": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok", "message": "Event ignored"}

    def test_webhook_organization_created_triggers_handler(
        self,
        client: TestClient,
        webhook_secret: str,
        organization_created_payload: dict,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """organization.created event calls the handler."""
        signature, payload_bytes = generate_workos_signature(
            organization_created_payload,
            webhook_secret,
        )

        with patch(
            "app.webhooks.workos.router.handle_organization_created",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post(
                "/webhooks/workos",
                content=payload_bytes,
                headers={
                    "WorkOS-Signature": signature,
                    "Content-Type": "application/json",
                },
            )

        assert response.status_code == 200
        mock_handler.assert_called_once()
        call_args = mock_handler.call_args[0]
        event = call_args[0]
        provisioning_service = call_args[1]
        assert event.event == "organization.created"
        assert event.data.id == "org_01XYZ789"
        assert event.data.name == "Acme Corp"
        assert provisioning_service is mock_provisioning_service
