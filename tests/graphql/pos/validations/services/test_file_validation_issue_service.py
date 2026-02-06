import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.data_exchange.models.enums import ExchangeFileStatus
from app.graphql.pos.validations.models import FileValidationIssue
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_validation_issue_service import (
    FileValidationIssueService,
)


class TestFileValidationIssueService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository: AsyncMock) -> FileValidationIssueService:
        return FileValidationIssueService(repository=mock_repository)

    @staticmethod
    def _create_mock_issue(
        validation_key: str = "required_field",
        column_name: str | None = "selling_branch_zip_code",
        row_number: int = 2,
        file_id: uuid.UUID | None = None,
        file_name: str = "test_file.csv",
        file_status: str = ExchangeFileStatus.PENDING.value,
    ) -> MagicMock:
        issue = MagicMock(spec=FileValidationIssue)
        issue.id = uuid.uuid4()
        issue.exchange_file_id = file_id or uuid.uuid4()
        issue.row_number = row_number
        issue.column_name = column_name
        issue.validation_key = validation_key
        issue.message = "Test error message"
        issue.row_data = {"field1": "value1", "field2": "value2"}

        # Mock exchange_file relationship
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        issue.exchange_file.file_name = file_name
        issue.exchange_file.status = file_status

        return issue

    @pytest.mark.asyncio
    async def test_get_pending_issues_grouped_by_type(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns issues grouped by ValidationType → file_id → validation_key."""
        file_id = uuid.uuid4()
        blocking_issue = self._create_mock_issue(
            validation_key="required_field",
            file_id=file_id,
        )
        warning_issue = self._create_mock_issue(
            validation_key="lot_order_detection",
            file_id=file_id,
        )

        mock_repository.get_by_pending_files.return_value = [
            blocking_issue,
            warning_issue,
        ]

        result = await service.get_pending_issues_grouped()

        assert ValidationType.STANDARD_VALIDATION in result
        assert ValidationType.VALIDATION_WARNING in result
        assert ValidationType.AI_POWERED_VALIDATION in result
        blocking = result[ValidationType.STANDARD_VALIDATION]
        assert file_id in blocking
        assert "required_field" in blocking[file_id]
        assert len(blocking[file_id]["required_field"]) == 1
        warning = result[ValidationType.VALIDATION_WARNING]
        assert file_id in warning
        assert "lot_order_detection" in warning[file_id]
        assert len(warning[file_id]["lot_order_detection"]) == 1
        assert len(result[ValidationType.AI_POWERED_VALIDATION]) == 0

    @pytest.mark.asyncio
    async def test_get_pending_issues_excludes_sent_files(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Issues from sent files not included (filtered by repository)."""
        # Repository returns only issues from pending files
        mock_repository.get_by_pending_files.return_value = []

        result = await service.get_pending_issues_grouped()

        mock_repository.get_by_pending_files.assert_called_once()
        assert len(result[ValidationType.STANDARD_VALIDATION]) == 0
        assert len(result[ValidationType.VALIDATION_WARNING]) == 0
        assert len(result[ValidationType.AI_POWERED_VALIDATION]) == 0


    @pytest.mark.asyncio
    async def test_get_pending_issues_includes_file_info(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Each issue has file_id and file_name from the relationship."""
        file_id = uuid.uuid4()
        issue = self._create_mock_issue(file_name="my_data.csv", file_id=file_id)
        mock_repository.get_by_pending_files.return_value = [issue]

        result = await service.get_pending_issues_grouped()

        blocking = result[ValidationType.STANDARD_VALIDATION]
        assert file_id in blocking
        issues = blocking[file_id]["required_field"]
        assert len(issues) == 1
        assert issues[0].exchange_file.file_name == "my_data.csv"

    @pytest.mark.asyncio
    async def test_get_pending_issues_grouped_by_key(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Issues are sub-grouped by validation_key within each file."""
        file_id = uuid.uuid4()
        required_field_issue_1 = self._create_mock_issue(
            validation_key="required_field",
            column_name="selling_branch_zip_code",
            file_id=file_id,
        )
        required_field_issue_2 = self._create_mock_issue(
            validation_key="required_field",
            column_name="transaction_date",
            file_id=file_id,
        )
        date_format_issue = self._create_mock_issue(
            validation_key="date_format",
            file_id=file_id,
        )
        warning_issue = self._create_mock_issue(
            validation_key="lot_order_detection",
            file_id=file_id,
        )

        mock_repository.get_by_pending_files.return_value = [
            required_field_issue_1,
            required_field_issue_2,
            date_format_issue,
            warning_issue,
        ]

        result = await service.get_pending_issues_grouped()

        blocking_file = result[ValidationType.STANDARD_VALIDATION][file_id]
        assert "required_field" in blocking_file
        assert "date_format" in blocking_file
        assert len(blocking_file["required_field"]) == 2
        assert len(blocking_file["date_format"]) == 1

        warning_file = result[ValidationType.VALIDATION_WARNING][file_id]
        assert "lot_order_detection" in warning_file
        assert len(warning_file["lot_order_detection"]) == 1

    @pytest.mark.asyncio
    async def test_get_pending_issues_separates_files(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Issues from different files are grouped under separate file_ids."""
        file_id_a = uuid.uuid4()
        file_id_b = uuid.uuid4()
        issue_a = self._create_mock_issue(
            validation_key="required_field",
            file_id=file_id_a,
            file_name="sales_jan.csv",
        )
        issue_b = self._create_mock_issue(
            validation_key="required_field",
            file_id=file_id_b,
            file_name="sales_feb.csv",
        )

        mock_repository.get_by_pending_files.return_value = [issue_a, issue_b]

        result = await service.get_pending_issues_grouped()

        blocking = result[ValidationType.STANDARD_VALIDATION]
        assert file_id_a in blocking
        assert file_id_b in blocking
        assert len(blocking[file_id_a]["required_field"]) == 1
        assert len(blocking[file_id_b]["required_field"]) == 1

    @pytest.mark.asyncio
    async def test_get_issue_by_id(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns single issue with row data."""
        issue = self._create_mock_issue()
        mock_repository.get_by_id.return_value = issue

        result = await service.get_by_id(issue.id)

        assert result is not None
        assert result.id == issue.id
        assert result.row_data == issue.row_data
        mock_repository.get_by_id.assert_called_once_with(issue.id)

    @pytest.mark.asyncio
    async def test_get_issue_by_id_not_found(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns None for non-existent issue."""
        mock_repository.get_by_id.return_value = None

        result = await service.get_by_id(uuid.uuid4())

        assert result is None


class TestGetFilteredIssues:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository: AsyncMock) -> FileValidationIssueService:
        return FileValidationIssueService(repository=mock_repository)

    @staticmethod
    def _create_mock_issue(
        validation_key: str = "required_field",
        file_id: uuid.UUID | None = None,
    ) -> MagicMock:
        issue = MagicMock(spec=FileValidationIssue)
        issue.id = uuid.uuid4()
        issue.exchange_file_id = file_id or uuid.uuid4()
        issue.validation_key = validation_key
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        return issue

    @pytest.mark.asyncio
    async def test_returns_issues_when_type_matches_blocking_key(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns issues when blocking type matches a blocking validation_key."""
        file_id = uuid.uuid4()
        mock_issues = [
            self._create_mock_issue("required_field", file_id),
            self._create_mock_issue("required_field", file_id),
        ]
        mock_repository.get_by_file_and_key.return_value = mock_issues

        result = await service.get_filtered_issues(
            ValidationType.STANDARD_VALIDATION, file_id, "required_field"
        )

        assert len(result) == 2
        mock_repository.get_by_file_and_key.assert_called_once_with(
            file_id, "required_field"
        )

    @pytest.mark.asyncio
    async def test_returns_issues_when_type_matches_warning_key(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns issues when warning type matches a warning validation_key."""
        file_id = uuid.uuid4()
        mock_issues = [self._create_mock_issue("lot_order_detection", file_id)]
        mock_repository.get_by_file_and_key.return_value = mock_issues

        result = await service.get_filtered_issues(
            ValidationType.VALIDATION_WARNING, file_id, "lot_order_detection"
        )

        assert len(result) == 1
        mock_repository.get_by_file_and_key.assert_called_once_with(
            file_id, "lot_order_detection"
        )

    @pytest.mark.asyncio
    async def test_returns_empty_when_type_does_not_match_key(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns empty list when validationType doesn't match the validation_key."""
        file_id = uuid.uuid4()

        # Requesting WARNING type but providing a BLOCKING key
        result = await service.get_filtered_issues(
            ValidationType.VALIDATION_WARNING, file_id, "required_field"
        )

        assert result == []
        mock_repository.get_by_file_and_key.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_issues_found(
        self,
        service: FileValidationIssueService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns empty list when repository returns no issues."""
        file_id = uuid.uuid4()
        mock_repository.get_by_file_and_key.return_value = []

        result = await service.get_filtered_issues(
            ValidationType.STANDARD_VALIDATION, file_id, "required_field"
        )

        assert result == []
