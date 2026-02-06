import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.tenant_provisioning.service import (
    ProvisioningResult,
    ProvisioningStatus,
)
from app.webhooks.workos.handlers import handle_organization_created
from app.webhooks.workos.schemas import WorkOSEvent, WorkOSOrganizationData


class TestHandleOrganizationCreated:
    @pytest.fixture
    def mock_provisioning_service(self) -> AsyncMock:
        mock: Any = AsyncMock()
        return mock

    @staticmethod
    def _create_event(
        org_id: str = "org_01XYZ789",
        org_name: str = "Acme Corp",
    ) -> WorkOSEvent:
        return WorkOSEvent(
            id="event_01ABC123",
            event="organization.created",
            created_at=datetime.now(timezone.utc),
            data=WorkOSOrganizationData(
                id=org_id,
                name=org_name,
                object="organization",
                external_id="ext-123",
                domains=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        )

    @pytest.mark.asyncio
    async def test_handle_organization_created_new_org(
        self,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """Full provisioning flow for new organization."""
        event = self._create_event(org_id="org_new_123", org_name="New Company")
        mock_provisioning_service.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.CREATED,
            tenant_id=uuid.uuid4(),
        )

        await handle_organization_created(event, mock_provisioning_service)

        mock_provisioning_service.provision.assert_called_once_with(
            org_id="org_new_123",
            org_name="New Company",
        )

    @pytest.mark.asyncio
    async def test_handle_organization_created_existing_org(
        self,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """Existing organization is logged but no error raised."""
        event = self._create_event(org_id="org_existing", org_name="Existing Corp")
        mock_provisioning_service.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.ALREADY_EXISTS,
            tenant_id=uuid.uuid4(),
        )

        # Should not raise
        await handle_organization_created(event, mock_provisioning_service)

        mock_provisioning_service.provision.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_organization_created_failure_logged(
        self,
        mock_provisioning_service: AsyncMock,
    ) -> None:
        """Provisioning failure is logged but does not raise."""
        event = self._create_event()
        mock_provisioning_service.provision.return_value = ProvisioningResult(
            status=ProvisioningStatus.FAILED,
            error="Database creation failed",
        )

        # Should not raise - webhook handlers should not fail
        await handle_organization_created(event, mock_provisioning_service)

        mock_provisioning_service.provision.assert_called_once()
