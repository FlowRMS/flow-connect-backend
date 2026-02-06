import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ExchangeFileStatus,
    ExchangeFileTargetOrg,
)
from app.graphql.pos.data_exchange.services.cross_tenant_delivery_service import (
    CrossTenantDeliveryService,
)


class TestCrossTenantDeliveryService:
    @pytest.fixture
    def mock_controller(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def service(self, mock_controller: MagicMock) -> CrossTenantDeliveryService:
        return CrossTenantDeliveryService(controller=mock_controller)

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        target_org_ids: list[uuid.UUID] | None = None,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.s3_key = f"exchange-files/{mock_file.org_id}/abc123.csv"
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_sha = "abc123"
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False
        mock_file.status = ExchangeFileStatus.SENT.value

        mock_targets = []
        for target_id in target_org_ids or []:
            target = MagicMock(spec=ExchangeFileTargetOrg)
            target.connected_org_id = target_id
            mock_targets.append(target)
        mock_file.target_organizations = mock_targets

        return mock_file

    @staticmethod
    def _create_mock_tenant(org_id: uuid.UUID, url: str) -> MagicMock:
        tenant = MagicMock()
        tenant.org_id = org_id
        tenant.url = url
        return tenant

    # Tenant resolution tests
    @pytest.mark.asyncio
    async def test_resolve_tenant_url_queries_subscription_db(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Resolves tenant URL by querying subscription database."""
        org_id = uuid.uuid4()
        expected_url = "tenant-abc"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected_url
        mock_session.execute.return_value = mock_result

        mock_controller.base_scoped_session.return_value.__aenter__.return_value = (
            mock_session
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        result = await service.resolve_tenant_url(org_id)

        assert result == expected_url
        mock_controller.base_scoped_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_resolve_tenant_url_returns_none_when_not_found(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Returns None when tenant is not found."""
        org_id = uuid.uuid4()

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        mock_controller.base_scoped_session.return_value.__aenter__.return_value = (
            mock_session
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        result = await service.resolve_tenant_url(org_id)

        assert result is None

    # Delivery tests
    @pytest.mark.asyncio
    async def test_deliver_files_creates_received_file_in_target_tenant(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Creates ReceivedExchangeFile record in target tenant's database."""
        target_org_id = uuid.uuid4()
        mock_file = self._create_mock_file(target_org_ids=[target_org_id])
        tenant_url = "target-tenant"

        # Mock tenant resolution
        mock_base_session = AsyncMock()
        mock_base_result = MagicMock()
        mock_base_result.scalar_one_or_none.return_value = tenant_url
        mock_base_session.execute.return_value = mock_base_result

        mock_controller.base_scoped_session.return_value.__aenter__.return_value = (
            mock_base_session
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        # Mock target tenant session - use MagicMock for sync attributes
        mock_target_session = MagicMock()
        mock_target_session.add = MagicMock()
        mock_target_session.flush = AsyncMock()

        # begin() returns an async context manager (not an async method)
        mock_begin_ctx = MagicMock()
        mock_begin_ctx.__aenter__ = AsyncMock(return_value=None)
        mock_begin_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_target_session.begin = MagicMock(return_value=mock_begin_ctx)

        mock_controller.scoped_session.return_value.__aenter__ = AsyncMock(
            return_value=mock_target_session
        )
        mock_controller.scoped_session.return_value.__aexit__ = AsyncMock(
            return_value=None
        )

        await service.deliver_files([mock_file])

        mock_controller.scoped_session.assert_called_with(tenant_url)
        mock_target_session.add.assert_called_once()
        mock_target_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_deliver_files_error_isolation(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Failure in one target doesn't block delivery to others."""
        target_org_id_1 = uuid.uuid4()
        target_org_id_2 = uuid.uuid4()
        mock_file = self._create_mock_file(
            target_org_ids=[target_org_id_1, target_org_id_2]
        )

        call_count = 0

        async def mock_base_scoped_session_enter(*args: object) -> AsyncMock:
            nonlocal call_count
            call_count += 1
            mock_session = AsyncMock()
            mock_result = MagicMock()
            # Alternate between tenant URLs
            mock_result.scalar_one_or_none.return_value = f"tenant-{call_count}"
            mock_session.execute.return_value = mock_result
            return mock_session

        mock_controller.base_scoped_session.return_value.__aenter__ = (
            mock_base_scoped_session_enter
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        # First target succeeds, second target fails
        scoped_call_count = 0

        async def mock_scoped_session_enter(*args: object) -> AsyncMock:
            nonlocal scoped_call_count
            scoped_call_count += 1
            mock_session = AsyncMock()
            mock_session.begin.return_value.__aenter__.return_value = None
            mock_session.begin.return_value.__aexit__.return_value = None
            if scoped_call_count == 1:
                return mock_session
            else:
                mock_session.flush.side_effect = Exception("Database error")
                return mock_session

        mock_controller.scoped_session.return_value.__aenter__ = (
            mock_scoped_session_enter
        )
        mock_controller.scoped_session.return_value.__aexit__.return_value = None

        # Should not raise - errors are isolated
        await service.deliver_files([mock_file])

        # Both targets should be attempted
        assert mock_controller.scoped_session.call_count == 2

    @pytest.mark.asyncio
    async def test_deliver_files_idempotent_on_duplicate(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Handles duplicate delivery gracefully via unique constraint."""
        target_org_id = uuid.uuid4()
        mock_file = self._create_mock_file(target_org_ids=[target_org_id])
        tenant_url = "target-tenant"

        mock_base_session = AsyncMock()
        mock_base_result = MagicMock()
        mock_base_result.scalar_one_or_none.return_value = tenant_url
        mock_base_session.execute.return_value = mock_base_result

        mock_controller.base_scoped_session.return_value.__aenter__.return_value = (
            mock_base_session
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        # Simulate unique constraint violation
        mock_target_session = AsyncMock()
        mock_target_session.begin.return_value.__aenter__.return_value = None
        mock_target_session.begin.return_value.__aexit__.return_value = None
        mock_target_session.flush.side_effect = IntegrityError(
            "duplicate key", {}, Exception()
        )

        mock_controller.scoped_session.return_value.__aenter__.return_value = (
            mock_target_session
        )
        mock_controller.scoped_session.return_value.__aexit__.return_value = None

        # Should not raise - idempotent behavior
        await service.deliver_files([mock_file])

    @pytest.mark.asyncio
    async def test_deliver_files_skips_when_tenant_not_found(
        self,
        service: CrossTenantDeliveryService,
        mock_controller: MagicMock,
    ) -> None:
        """Skips delivery when target tenant is not found."""
        target_org_id = uuid.uuid4()
        mock_file = self._create_mock_file(target_org_ids=[target_org_id])

        mock_base_session = AsyncMock()
        mock_base_result = MagicMock()
        mock_base_result.scalar_one_or_none.return_value = None  # Tenant not found
        mock_base_session.execute.return_value = mock_base_result

        mock_controller.base_scoped_session.return_value.__aenter__.return_value = (
            mock_base_session
        )
        mock_controller.base_scoped_session.return_value.__aexit__.return_value = None

        await service.deliver_files([mock_file])

        # Should not attempt to open target tenant session
        mock_controller.scoped_session.assert_not_called()


class TestExchangeFileServiceSendWithDelivery:
    """Tests for send_pending_files() integration with delivery service."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_delivery_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_user_org_id.return_value = uuid.uuid4()
        return repo

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "user_01KEHRJ8JTMM2NZ2MQFX30C5T3"
        return auth_info

    @pytest.mark.asyncio
    async def test_send_pending_files_triggers_delivery(
        self,
        mock_repository: AsyncMock,
        mock_delivery_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> None:
        """Delivery is triggered after files are marked as SENT."""
        from app.graphql.pos.data_exchange.services.exchange_file_service import (
            ExchangeFileService,
        )

        org_id = mock_user_org_repository.get_user_org_id.return_value
        target_org_id = uuid.uuid4()

        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id
        mock_file.status = ExchangeFileStatus.PENDING.value
        target = MagicMock(spec=ExchangeFileTargetOrg)
        target.connected_org_id = target_org_id
        mock_file.target_organizations = [target]

        mock_repository.list_pending_for_org.return_value = [mock_file]
        mock_repository.update_pending_to_sent.return_value = 1

        mock_validation_issue_repository = AsyncMock()
        mock_validation_issue_repository.has_blocking_issues_for_pending_files.return_value = (
            False
        )

        service = ExchangeFileService(
            repository=mock_repository,
            s3_service=AsyncMock(),
            user_org_repository=mock_user_org_repository,
            org_search_repository=AsyncMock(),
            validation_issue_repository=mock_validation_issue_repository,
            auth_info=mock_auth_info,
            delivery_service=mock_delivery_service,
        )

        count = await service.send_pending_files()

        assert count == 1
        mock_repository.list_pending_for_org.assert_called_once_with(org_id)
        mock_repository.update_pending_to_sent.assert_called_once_with(org_id)
        mock_delivery_service.deliver_files.assert_called_once_with([mock_file])
