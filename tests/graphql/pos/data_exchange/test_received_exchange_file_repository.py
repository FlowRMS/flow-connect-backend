import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.data_exchange.models import (
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)
from app.graphql.pos.data_exchange.repositories.received_exchange_file_repository import (
    ReceivedExchangeFileRepository,
)


class TestReceivedExchangeFileRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> ReceivedExchangeFileRepository:
        return ReceivedExchangeFileRepository(session=mock_session)

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

    @pytest.mark.asyncio
    async def test_create_file(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new received file record and flushes to session."""
        file = self._create_mock_file()

        result = await repository.create(file)

        mock_session.add.assert_called_once_with(file)
        mock_session.flush.assert_called_once()
        assert result == file

    @pytest.mark.asyncio
    async def test_list_for_org_returns_files(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns all received files for the organization."""
        org_id = uuid.uuid4()
        mock_files = [
            self._create_mock_file(org_id=org_id),
            self._create_mock_file(org_id=org_id),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_files
        mock_session.execute.return_value = mock_result

        result = await repository.list_for_org(org_id)

        assert len(result) == 2
        assert result == mock_files
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_for_org_with_period_filter(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Filters received files by period."""
        org_id = uuid.uuid4()
        mock_files = [self._create_mock_file(org_id=org_id)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_files
        mock_session.execute.return_value = mock_result

        result = await repository.list_for_org(org_id, period="2026-Q1")

        assert result == mock_files
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_for_org_with_senders_filter(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Filters received files by sender org IDs."""
        org_id = uuid.uuid4()
        sender_id = uuid.uuid4()
        mock_files = [self._create_mock_file(org_id=org_id, sender_org_id=sender_id)]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_files
        mock_session.execute.return_value = mock_result

        result = await repository.list_for_org(org_id, senders=[sender_id])

        assert result == mock_files
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_file(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns file when found by id and org_id."""
        org_id = uuid.uuid4()
        file_id = uuid.uuid4()
        mock_file = self._create_mock_file(org_id=org_id)
        mock_file.id = file_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_file
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(file_id, org_id)

        assert result == mock_file
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when file doesn't exist."""
        org_id = uuid.uuid4()
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(file_id, org_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_status(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Updates file status and returns True."""
        org_id = uuid.uuid4()
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.update_status(
            file_id, org_id, ReceivedExchangeFileStatus.DOWNLOADED.value
        )

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_returns_false_when_not_found(
        self,
        repository: ReceivedExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when file doesn't exist."""
        org_id = uuid.uuid4()
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.update_status(
            file_id, org_id, ReceivedExchangeFileStatus.DOWNLOADED.value
        )

        assert result is False
