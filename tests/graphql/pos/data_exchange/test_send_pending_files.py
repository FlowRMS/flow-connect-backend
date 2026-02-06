import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.data_exchange.exceptions import (
    HasBlockingValidationIssuesError,
    NoPendingFilesError,
)
from app.graphql.pos.data_exchange.services.exchange_file_service import (
    ExchangeFileService,
)


class TestSendPendingFiles:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_s3_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_user_org_id.return_value = uuid.uuid4()
        return repo

    @pytest.fixture
    def mock_validation_issue_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_org_search_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "user_01KEHRJ8JTMM2NZ2MQFX30C5T3"
        auth_info.flow_user_id = uuid.uuid4()
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_org_search_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> ExchangeFileService:
        return ExchangeFileService(
            repository=mock_repository,
            s3_service=mock_s3_service,
            user_org_repository=mock_user_org_repository,
            org_search_repository=mock_org_search_repository,
            validation_issue_repository=mock_validation_issue_repository,
            auth_info=mock_auth_info,
        )

    @pytest.mark.asyncio
    async def test_send_pending_files_success(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns count when no blocking issues exist."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_validation_issue_repository.has_blocking_issues_for_pending_files.return_value = (
            False
        )
        mock_repository.update_pending_to_sent.return_value = 3

        result = await service.send_pending_files()

        assert result == 3
        mock_validation_issue_repository.has_blocking_issues_for_pending_files.assert_called_once_with(
            org_id
        )
        mock_repository.update_pending_to_sent.assert_called_once_with(org_id)

    @pytest.mark.asyncio
    async def test_send_pending_files_with_blocking_issues(
        self,
        service: ExchangeFileService,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Raises HasBlockingValidationIssuesError when blocking issues exist."""
        mock_validation_issue_repository.has_blocking_issues_for_pending_files.return_value = (
            True
        )

        with pytest.raises(HasBlockingValidationIssuesError):
            await service.send_pending_files()

    @pytest.mark.asyncio
    async def test_send_pending_files_no_pending(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Raises NoPendingFilesError when no pending files exist."""
        mock_validation_issue_repository.has_blocking_issues_for_pending_files.return_value = (
            False
        )
        mock_repository.update_pending_to_sent.return_value = 0

        with pytest.raises(NoPendingFilesError):
            await service.send_pending_files()
