import datetime
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.dashboard.services.dashboard_glance_service import (
    DashboardGlanceService,
)


class TestDashboardGlanceService:
    @pytest.fixture
    def mock_validation_issue_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_exchange_file_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_user_org_id.return_value = uuid.uuid4()
        return repo

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "user_test_123"
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> DashboardGlanceService:
        return DashboardGlanceService(
            validation_issue_repository=mock_validation_issue_repository,
            connection_repository=mock_connection_repository,
            exchange_file_repository=mock_exchange_file_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )

    @pytest.mark.asyncio
    async def test_get_glance_returns_all_metrics(
        self,
        service: DashboardGlanceService,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
    ) -> None:
        """Returns response with all metrics populated."""
        mock_validation_issue_repository.count_blocking_issues_for_all_pending_files.return_value = 5
        mock_connection_repository.count_by_status.side_effect = [3, 1]

        mock_file = MagicMock()
        mock_file.created_at = datetime.datetime(2026, 1, 28, 14, 30, tzinfo=datetime.UTC)
        mock_file.row_count = 1234
        mock_exchange_file_repository.get_last_sent_file.return_value = mock_file

        result = await service.get_glance()

        assert result.issues.blocking_sends_count == 5
        assert result.partners.connected_count == 3
        assert result.partners.pending_count == 1
        assert result.messages.unread_count == 0
        assert result.last_delivery is not None
        assert result.last_delivery.date == mock_file.created_at
        assert result.last_delivery.record_count == 1234

    @pytest.mark.asyncio
    async def test_get_glance_no_issues(
        self,
        service: DashboardGlanceService,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
    ) -> None:
        """Issues count is 0 when no blocking issues."""
        mock_validation_issue_repository.count_blocking_issues_for_all_pending_files.return_value = 0
        mock_connection_repository.count_by_status.side_effect = [0, 0]
        mock_exchange_file_repository.get_last_sent_file.return_value = None

        result = await service.get_glance()

        assert result.issues.blocking_sends_count == 0

    @pytest.mark.asyncio
    async def test_get_glance_no_partners(
        self,
        service: DashboardGlanceService,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
    ) -> None:
        """Both connected and pending are 0 when no connections."""
        mock_validation_issue_repository.count_blocking_issues_for_all_pending_files.return_value = 0
        mock_connection_repository.count_by_status.side_effect = [0, 0]
        mock_exchange_file_repository.get_last_sent_file.return_value = None

        result = await service.get_glance()

        assert result.partners.connected_count == 0
        assert result.partners.pending_count == 0

    @pytest.mark.asyncio
    async def test_get_glance_no_deliveries(
        self,
        service: DashboardGlanceService,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
    ) -> None:
        """Last delivery is None when no sent files."""
        mock_validation_issue_repository.count_blocking_issues_for_all_pending_files.return_value = 0
        mock_connection_repository.count_by_status.side_effect = [0, 0]
        mock_exchange_file_repository.get_last_sent_file.return_value = None

        result = await service.get_glance()

        assert result.last_delivery is None

    @pytest.mark.asyncio
    async def test_get_glance_messages_always_zero(
        self,
        service: DashboardGlanceService,
        mock_validation_issue_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_exchange_file_repository: AsyncMock,
    ) -> None:
        """Messages unread count is always 0 (hardcoded)."""
        mock_validation_issue_repository.count_blocking_issues_for_all_pending_files.return_value = 10
        mock_connection_repository.count_by_status.side_effect = [5, 2]

        mock_file = MagicMock()
        mock_file.created_at = datetime.datetime(2026, 1, 28, tzinfo=datetime.UTC)
        mock_file.row_count = 500
        mock_exchange_file_repository.get_last_sent_file.return_value = mock_file

        result = await service.get_glance()

        assert result.messages.unread_count == 0
