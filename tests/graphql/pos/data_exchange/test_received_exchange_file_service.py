import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.data_exchange.exceptions import ReceivedExchangeFileNotFoundError
from app.graphql.pos.data_exchange.models import (
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)
from app.graphql.pos.data_exchange.services.received_exchange_file_service import (
    ReceivedExchangeFileService,
)


class TestReceivedExchangeFileService:
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
        mock_auth_info: MagicMock,
    ) -> ReceivedExchangeFileService:
        return ReceivedExchangeFileService(
            repository=mock_repository,
            s3_service=mock_s3_service,
            user_org_repository=mock_user_org_repository,
            org_search_repository=mock_org_search_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        sender_org_id: uuid.UUID | None = None,
        status: str = ReceivedExchangeFileStatus.NEW.value,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ReceivedExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.sender_org_id = sender_org_id or uuid.uuid4()
        mock_file.s3_key = f"exchange-files/{mock_file.sender_org_id}/abc123.csv"
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_sha = "abc123"
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False
        mock_file.status = status
        return mock_file

    # List files tests
    @pytest.mark.asyncio
    async def test_list_received_files_returns_files(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns received files for the user's organization."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_files = [
            self._create_mock_file(org_id=org_id),
            self._create_mock_file(org_id=org_id),
        ]
        mock_repository.list_for_org.return_value = mock_files

        result = await service.list_received_files()

        assert len(result) == 2
        mock_repository.list_for_org.assert_called_once_with(
            org_id, period=None, senders=None, is_pos=None, is_pot=None
        )

    @pytest.mark.asyncio
    async def test_list_received_files_with_period_filter(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Filters files by reporting period."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_repository.list_for_org.return_value = []

        await service.list_received_files(period="2026-Q1")

        mock_repository.list_for_org.assert_called_once_with(
            org_id, period="2026-Q1", senders=None, is_pos=None, is_pot=None
        )

    @pytest.mark.asyncio
    async def test_list_received_files_with_senders_filter(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Filters files by sender org IDs."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        sender_ids = [uuid.uuid4(), uuid.uuid4()]
        mock_repository.list_for_org.return_value = []

        await service.list_received_files(senders=sender_ids)

        mock_repository.list_for_org.assert_called_once_with(
            org_id, period=None, senders=sender_ids, is_pos=None, is_pot=None
        )

    @pytest.mark.asyncio
    async def test_list_received_files_with_type_filters(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Filters files by is_pos and is_pot flags."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_repository.list_for_org.return_value = []

        await service.list_received_files(is_pos=True, is_pot=False)

        mock_repository.list_for_org.assert_called_once_with(
            org_id, period=None, senders=None, is_pos=True, is_pot=False
        )

    # Download file tests
    @pytest.mark.asyncio
    async def test_download_file_returns_presigned_url(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns presigned URL for file download."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        file_id = uuid.uuid4()
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.get_by_id.return_value = mock_file
        mock_s3_service.generate_presigned_url.return_value = "https://s3.example.com/presigned"
        mock_repository.update_status.return_value = True

        result = await service.download_file(file_id)

        assert result == "https://s3.example.com/presigned"
        mock_s3_service.generate_presigned_url.assert_called_once_with(mock_file.s3_key)

    @pytest.mark.asyncio
    async def test_download_file_updates_status_to_downloaded(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Marks file as downloaded after generating URL."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        file_id = uuid.uuid4()
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.get_by_id.return_value = mock_file
        mock_s3_service.generate_presigned_url.return_value = "https://s3.example.com/presigned"
        mock_repository.update_status.return_value = True

        await service.download_file(file_id)

        mock_repository.update_status.assert_called_once_with(
            file_id, org_id, ReceivedExchangeFileStatus.DOWNLOADED.value
        )

    @pytest.mark.asyncio
    async def test_download_file_raises_when_not_found(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises exception when file doesn't exist."""
        file_id = uuid.uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ReceivedExchangeFileNotFoundError):
            await service.download_file(file_id)

    @pytest.mark.asyncio
    async def test_download_file_scoped_to_user_org(
        self,
        service: ReceivedExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Queries file using user's org_id for security."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        file_id = uuid.uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ReceivedExchangeFileNotFoundError):
            await service.download_file(file_id)

        mock_repository.get_by_id.assert_called_once_with(file_id, org_id)
