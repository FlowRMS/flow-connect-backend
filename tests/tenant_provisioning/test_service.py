import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from commons.db.models.tenant import Tenant

from app.tenant_provisioning.service import (
    DatabaseServiceProtocol,
    MigrationServiceProtocol,
    ProvisioningStatus,
    TenantProvisioningService,
)


class TestTenantProvisioningService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_database_service(self) -> DatabaseServiceProtocol:
        mock: Any = AsyncMock()
        return mock

    @pytest.fixture
    def mock_migration_service(self) -> MigrationServiceProtocol:
        mock: Any = AsyncMock()
        return mock

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_database_service: DatabaseServiceProtocol,
        mock_migration_service: MigrationServiceProtocol,
    ) -> TenantProvisioningService:
        return TenantProvisioningService(
            repository=mock_repository,
            database_service=mock_database_service,
            migration_service=mock_migration_service,
            db_connection_url="postgresql://app_user:pass@db.example.com",
            db_host="db.example.com",
            db_ro_host="db-ro.example.com",
            db_username="app_user",
        )

    @staticmethod
    def _create_mock_tenant(
        org_id: str = "org_123",
        url: str = "acme-corp",
        initialize: bool = False,
    ) -> MagicMock:
        tenant = MagicMock(spec=Tenant)
        tenant.id = uuid.uuid4()
        tenant.org_id = org_id
        tenant.url = url
        tenant.initialize = initialize
        return tenant

    @pytest.mark.asyncio
    async def test_provision_new_tenant_creates_all_resources(
        self,
        service: TenantProvisioningService,
        mock_repository: AsyncMock,
        mock_database_service: AsyncMock,
        mock_migration_service: AsyncMock,
    ) -> None:
        """Full provisioning flow for new organization."""
        mock_repository.get_by_org_id.return_value = None
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = self._create_mock_tenant()
        mock_database_service.database_exists.return_value = False
        mock_migration_service.run_migrations.return_value = "abc123"

        result = await service.provision(org_id="org_123", org_name="Acme Corp")

        assert result.status == ProvisioningStatus.CREATED
        mock_repository.get_by_org_id.assert_called_once_with("org_123")
        mock_repository.create.assert_called_once()
        mock_database_service.create_database.assert_called_once()
        mock_migration_service.run_migrations.assert_called_once()
        mock_repository.update_initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_provision_existing_tenant_skips_creation(
        self,
        service: TenantProvisioningService,
        mock_repository: AsyncMock,
        mock_database_service: AsyncMock,
        mock_migration_service: AsyncMock,
    ) -> None:
        """No-op if tenant already exists for org_id."""
        existing_tenant = self._create_mock_tenant(initialize=True)
        mock_repository.get_by_org_id.return_value = existing_tenant

        result = await service.provision(org_id="org_123", org_name="Acme Corp")

        assert result.status == ProvisioningStatus.ALREADY_EXISTS
        mock_repository.create.assert_not_called()
        mock_database_service.create_database.assert_not_called()
        mock_migration_service.run_migrations.assert_not_called()

    @pytest.mark.asyncio
    async def test_provision_existing_db_runs_migrations(
        self,
        service: TenantProvisioningService,
        mock_repository: AsyncMock,
        mock_database_service: AsyncMock,
        mock_migration_service: AsyncMock,
    ) -> None:
        """If database exists, skip creation but run migrations."""
        mock_repository.get_by_org_id.return_value = None
        mock_repository.get_by_url.return_value = None
        mock_repository.create.return_value = self._create_mock_tenant()
        mock_database_service.database_exists.return_value = True
        mock_migration_service.run_migrations.return_value = "abc123"

        result = await service.provision(org_id="org_123", org_name="Acme Corp")

        assert result.status == ProvisioningStatus.CREATED
        mock_database_service.create_database.assert_not_called()
        mock_migration_service.run_migrations.assert_called_once()


class TestGenerateTenantUrl:
    """Tests for the static generate_tenant_url method."""

    def test_simple_name(self) -> None:
        """Simple org name converts to lowercase with hyphens."""
        result = TenantProvisioningService.generate_tenant_url("Acme Corp")
        assert result == "acme-corp"

    def test_special_characters_removed(self) -> None:
        """Special characters are removed from org name."""
        result = TenantProvisioningService.generate_tenant_url("Acme's & Co. (LLC)")
        assert result == "acmes-co-llc"

    def test_multiple_spaces_collapsed(self) -> None:
        """Multiple spaces become single hyphen."""
        result = TenantProvisioningService.generate_tenant_url("Acme    Corp    Inc")
        assert result == "acme-corp-inc"

    def test_leading_trailing_hyphens_removed(self) -> None:
        """Leading and trailing hyphens are stripped."""
        result = TenantProvisioningService.generate_tenant_url("  Acme Corp  ")
        assert result == "acme-corp"

    def test_unicode_handled(self) -> None:
        """Unicode characters are transliterated or removed."""
        result = TenantProvisioningService.generate_tenant_url("Ñoño Café")
        # Should handle accented characters gracefully
        assert "cafe" in result.lower() or "caf" in result.lower()
