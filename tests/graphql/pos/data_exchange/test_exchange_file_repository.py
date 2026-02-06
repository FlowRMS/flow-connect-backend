import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.data_exchange.models import ExchangeFile, ExchangeFileStatus
from app.graphql.pos.data_exchange.repositories.exchange_file_repository import (
    ExchangeFileRepository,
)


class TestExchangeFileRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> ExchangeFileRepository:
        return ExchangeFileRepository(session=mock_session)

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        file_sha: str = "abc123",
        status: str = ExchangeFileStatus.PENDING.value,
        row_count: int = 100,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.file_sha = file_sha
        mock_file.status = status
        mock_file.row_count = row_count
        mock_file.target_organizations = []
        return mock_file

    @pytest.mark.asyncio
    async def test_create_file(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new file record and flushes to session."""
        file = self._create_mock_file()

        result = await repository.create(file)

        mock_session.add.assert_called_once_with(file)
        mock_session.flush.assert_called_once()
        assert result == file

    @pytest.mark.asyncio
    async def test_get_by_id_returns_file(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns file when found by id."""
        file_id = uuid.uuid4()
        mock_file = self._create_mock_file()
        mock_file.id = file_id

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_file
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(file_id)

        assert result == mock_file
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when file doesn't exist."""
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(file_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_list_pending_for_org(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns all pending files for the organization."""
        org_id = uuid.uuid4()
        mock_files = [
            self._create_mock_file(org_id=org_id),
            self._create_mock_file(org_id=org_id),
        ]

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = (
            mock_files
        )
        mock_session.execute.return_value = mock_result

        result = await repository.list_pending_for_org(org_id)

        assert len(result) == 2
        assert result == mock_files
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_has_pending_with_sha_and_target_returns_true(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns True when pending file with SHA targets specified org."""
        org_id = uuid.uuid4()
        target_org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        mock_session.execute.return_value = mock_result

        result = await repository.has_pending_with_sha_and_target(
            org_id, "abc123", [target_org_id]
        )

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_has_pending_with_sha_and_target_returns_false(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when no pending file with SHA targets specified org."""
        org_id = uuid.uuid4()
        target_org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.has_pending_with_sha_and_target(
            org_id, "abc123", [target_org_id]
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_pending_file(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Deletes pending file and returns True."""
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(file_id)

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when file doesn't exist."""
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(file_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_pending_stats(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns file_count and total_rows for pending files."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.one_or_none.return_value = (3, 1500)
        mock_session.execute.return_value = mock_result

        file_count, total_rows = await repository.get_pending_stats(org_id)

        assert file_count == 3
        assert total_rows == 1500
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_pending_stats_returns_zeros_when_no_files(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns (0, 0) when no pending files exist."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        file_count, total_rows = await repository.get_pending_stats(org_id)

        assert file_count == 0
        assert total_rows == 0

    @pytest.mark.asyncio
    async def test_get_last_sent_file_returns_file(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns the most recent sent file."""
        org_id = uuid.uuid4()
        mock_file = self._create_mock_file(
            org_id=org_id, status=ExchangeFileStatus.SENT.value
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_file
        mock_session.execute.return_value = mock_result

        result = await repository.get_last_sent_file(org_id)

        assert result == mock_file
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_last_sent_file_returns_none_when_no_sent_files(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when no sent files exist."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_last_sent_file(org_id)

        assert result is None
