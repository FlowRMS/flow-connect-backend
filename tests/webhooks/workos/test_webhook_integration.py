"""
Integration test simulating the full WorkOS webhook flow.

This test simulates what happens when WorkOS sends an organization.created
webhook to our endpoint, without requiring a running server or actual
WorkOS integration.
"""

import uuid
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.tenant_provisioning.service import (
    ProvisioningResult,
    ProvisioningStatus,
)
from app.webhooks.workos.router import create_workos_webhook_router
from tests.webhooks.workos.conftest import generate_workos_signature


class TestWebhookIntegration:
    """Simulates the full webhook flow from WorkOS to tenant provisioning."""

    @pytest.fixture
    def webhook_secret(self) -> str:
        return "whsec_test_secret_for_integration"

    @pytest.fixture
    def mock_provisioning_service(self) -> AsyncMock:
        mock: Any = AsyncMock()
        mock.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.CREATED,
            tenant_id=uuid.uuid4(),
        )
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

    def test_full_webhook_flow_creates_tenant(
        self,
        client: TestClient,
        webhook_secret: str,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """
        Simulates WorkOS sending organization.created webhook.

        Verifies:
        1. Signature is validated
        2. Event is parsed correctly
        3. Provisioning service is called with correct params
        4. Response is 200 OK
        """
        payload = {
            "id": "event_integration_test",
            "event": "organization.created",
            "created_at": "2026-01-27T15:00:00Z",
            "data": {
                "id": "org_integration_123",
                "name": "Integration Test Corp",
                "object": "organization",
                "external_id": "ext-integration",
                "domains": [],
                "created_at": "2026-01-27T15:00:00Z",
                "updated_at": "2026-01-27T15:00:00Z",
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
        assert response.json() == {"status": "ok"}

        # Verify provisioning was called with correct parameters
        mock_provisioning_service.provision.assert_called_once_with(
            org_id="org_integration_123",
            org_name="Integration Test Corp",
        )

    def test_webhook_flow_existing_tenant_succeeds(
        self,
        client: TestClient,
        webhook_secret: str,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """Webhook succeeds even when tenant already exists."""
        mock_provisioning_service.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.ALREADY_EXISTS,
            tenant_id=uuid.uuid4(),
        )

        payload = {
            "id": "event_existing_test",
            "event": "organization.created",
            "created_at": "2026-01-27T15:00:00Z",
            "data": {
                "id": "org_existing_456",
                "name": "Existing Corp",
                "object": "organization",
                "external_id": None,
                "domains": [],
                "created_at": "2026-01-27T15:00:00Z",
                "updated_at": "2026-01-27T15:00:00Z",
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

        # Should still return 200 - webhook was processed successfully
        assert response.status_code == 200

    def test_webhook_flow_provisioning_failure_still_returns_200(
        self,
        client: TestClient,
        webhook_secret: str,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """
        Webhook returns 200 even if provisioning fails.

        This is important because WorkOS will retry on non-200 responses.
        We don't want retries for provisioning failures - they should be
        handled internally.
        """
        mock_provisioning_service.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.FAILED,
            error="Database creation failed",
        )

        payload = {
            "id": "event_failure_test",
            "event": "organization.created",
            "created_at": "2026-01-27T15:00:00Z",
            "data": {
                "id": "org_failure_789",
                "name": "Failure Corp",
                "object": "organization",
                "external_id": None,
                "domains": [],
                "created_at": "2026-01-27T15:00:00Z",
                "updated_at": "2026-01-27T15:00:00Z",
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

        # Should return 200 to prevent WorkOS retries
        assert response.status_code == 200
