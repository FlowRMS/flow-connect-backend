import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from commons.db.models.tenant import Tenant
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenant_provisioning.repository import TenantRepository


class TestTenantRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> TenantRepository:
        return TenantRepository(session=mock_session)

    @staticmethod
    def _create_mock_tenant(
        org_id: str = "org_123",
        name: str = "Test Org",
        url: str = "test-org",
        initialize: bool = False,
    ) -> MagicMock:
        tenant = MagicMock(spec=Tenant)
        tenant.id = uuid.uuid4()
        tenant.org_id = org_id
        tenant.name = name
        tenant.url = url
        tenant.initialize = initialize
        tenant.database = "db-host.example.com"
        tenant.read_only_database = "db-ro-host.example.com"
        tenant.username = "db_user"
        tenant.alembic_version = ""
        return tenant

    @pytest.mark.asyncio
    async def test_get_by_org_id_found(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns tenant when org_id exists."""
        mock_tenant = self._create_mock_tenant(org_id="org_123")
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_id("org_123")

        assert result is not None
        assert result.org_id == "org_123"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_org_id_not_found(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when org_id doesn't exist."""
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_id("nonexistent_org")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_tenant(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new tenant row with correct fields."""
        mock_tenant = self._create_mock_tenant()

        result = await repository.create(mock_tenant)

        assert result == mock_tenant
        mock_session.add.assert_called_once_with(mock_tenant)
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_initialize_flag(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Sets initialize=True after provisioning."""
        tenant_id = uuid.uuid4()
        mock_tenant = self._create_mock_tenant()
        mock_tenant.id = tenant_id
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_session.execute.return_value = mock_result

        await repository.update_initialize(tenant_id, initialize=True)

        assert mock_tenant.initialize is True
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_url_found(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns tenant when url exists."""
        mock_tenant = self._create_mock_tenant(url="acme-corp")
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = mock_tenant
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_url("acme-corp")

        assert result is not None
        assert result.url == "acme-corp"

    @pytest.mark.asyncio
    async def test_get_by_url_not_found(
        self,
        repository: TenantRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when url doesn't exist."""
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_url("nonexistent")

        assert result is None
