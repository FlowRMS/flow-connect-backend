import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.validations.models import FileValidationIssue
from app.graphql.pos.validations.repositories.file_validation_issue_repository import (
    FileValidationIssueRepository,
)


class TestFileValidationIssueRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> FileValidationIssueRepository:
        return FileValidationIssueRepository(session=mock_session)

    @staticmethod
    def _create_mock_issue(
        exchange_file_id: uuid.UUID | None = None,
        row_number: int = 2,
        validation_key: str = "required_field",
    ) -> MagicMock:
        mock_issue = MagicMock(spec=FileValidationIssue)
        mock_issue.id = uuid.uuid4()
        mock_issue.exchange_file_id = exchange_file_id or uuid.uuid4()
        mock_issue.row_number = row_number
        mock_issue.column_name = "field"
        mock_issue.validation_key = validation_key
        mock_issue.message = "Test error message"
        return mock_issue

    @pytest.mark.asyncio
    async def test_create_issues_bulk(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Create multiple issues for a file."""
        file_id = uuid.uuid4()
        issues = [
            self._create_mock_issue(exchange_file_id=file_id, row_number=2),
            self._create_mock_issue(exchange_file_id=file_id, row_number=3),
            self._create_mock_issue(exchange_file_id=file_id, row_number=4),
        ]

        await repository.create_bulk(issues)

        assert mock_session.add_all.called
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_issues_by_file_id(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Get all issues for a file."""
        file_id = uuid.uuid4()
        mock_issues = [
            self._create_mock_issue(exchange_file_id=file_id, row_number=2),
            self._create_mock_issue(exchange_file_id=file_id, row_number=3),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_issues
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_file_id(file_id)

        assert len(result) == 2
        assert result == mock_issues
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_issues_by_file_id(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Clear issues before re-validation."""
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 5
        mock_session.execute.return_value = mock_result

        result = await repository.delete_by_file_id(file_id)

        assert result == 5
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_blocking_issues(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Count only STANDARD_VALIDATION issues."""
        file_id = uuid.uuid4()
        blocking_keys = ["required_field", "date_format", "numeric_field"]

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        result = await repository.count_blocking_issues(file_id, blocking_keys)

        assert result == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_blocking_issues_for_all_pending_files(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns total blocking issue count across all pending files."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 7
        mock_session.execute.return_value = mock_result

        result = await repository.count_blocking_issues_for_all_pending_files(org_id)

        assert result == 7
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_blocking_issues_for_all_pending_files_returns_zero(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns 0 when no blocking issues exist."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        result = await repository.count_blocking_issues_for_all_pending_files(org_id)

        assert result == 0


class TestGetByFileAndKey:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> FileValidationIssueRepository:
        return FileValidationIssueRepository(session=mock_session)

    @staticmethod
    def _create_mock_issue(
        exchange_file_id: uuid.UUID,
        validation_key: str = "required_field",
        row_number: int = 2,
    ) -> MagicMock:
        mock_issue = MagicMock(spec=FileValidationIssue)
        mock_issue.id = uuid.uuid4()
        mock_issue.exchange_file_id = exchange_file_id
        mock_issue.row_number = row_number
        mock_issue.validation_key = validation_key
        mock_issue.exchange_file = MagicMock()
        mock_issue.exchange_file.id = exchange_file_id
        return mock_issue

    @pytest.mark.asyncio
    async def test_returns_issues_matching_file_and_key(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns issues for the given file_id and validation_key."""
        file_id = uuid.uuid4()
        mock_issues = [
            self._create_mock_issue(file_id, "required_field", row_number=1),
            self._create_mock_issue(file_id, "required_field", row_number=5),
        ]

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = (
            mock_issues
        )
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_file_and_key(file_id, "required_field")

        assert len(result) == 2
        assert result == mock_issues
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_matches(
        self,
        repository: FileValidationIssueRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns empty list when no issues match."""
        file_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_file_and_key(file_id, "nonexistent_key")

        assert result == []
