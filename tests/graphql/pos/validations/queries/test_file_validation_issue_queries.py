import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.queries.file_validation_issue_queries import (
    FileValidationIssueQueries,
)
from app.graphql.pos.validations.strawberry.file_validation_issue_types import (
    FileGroupResponse,
    FileValidationIssueLiteResponse,
    FileValidationIssueResponse,
    FileValidationIssuesResponse,
    ValidationIssueGroupResponse,
    ValidationKeyGroupResponse,
)


class TestFileValidationIssueResponse:
    @staticmethod
    def _create_mock_issue(
        validation_key: str = "required_field",
        column_name: str | None = "selling_branch_zip_code",
        file_name: str = "test_file.csv",
        row_data: dict | None = None,
    ) -> MagicMock:
        issue = MagicMock()
        issue.id = uuid.uuid4()
        issue.exchange_file_id = uuid.uuid4()
        issue.row_number = 2
        issue.column_name = column_name
        issue.validation_key = validation_key
        issue.message = "Test error message"
        issue.row_data = row_data
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        issue.exchange_file.file_name = file_name
        return issue

    def test_from_model_maps_all_fields(self) -> None:
        """FileValidationIssueResponse.from_model maps all fields correctly."""
        issue = self._create_mock_issue(
            validation_key="required_field",
            column_name="quantity_units_sold",
            file_name="data.csv",
            row_data={"field1": "value1", "field2": 123},
        )

        result = FileValidationIssueResponse.from_model(issue)

        assert str(result.id) == str(issue.id)
        assert result.row_number == 2
        assert result.column_name == "quantity_units_sold"
        assert result.validation_key == "required_field"
        assert result.message == "Test error message"
        assert result.title == "Quantity missing"
        assert str(result.file_id) == str(issue.exchange_file_id)
        assert result.file_name == "data.csv"
        assert result.row_data == {"field1": "value1", "field2": 123}

    def test_from_model_handles_none_column_name(self) -> None:
        """FileValidationIssueResponse.from_model handles None column_name."""
        issue = self._create_mock_issue(column_name=None)

        result = FileValidationIssueResponse.from_model(issue)

        assert result.column_name is None

    def test_from_model_does_not_include_validation_type(self) -> None:
        """FileValidationIssueResponse does not include validationType (DD-3)."""
        issue = self._create_mock_issue(validation_key="required_field")

        result = FileValidationIssueResponse.from_model(issue)

        assert not hasattr(result, "validation_type")


class TestFileValidationIssueLiteResponse:
    @staticmethod
    def _create_mock_issue(
        validation_key: str = "required_field",
        column_name: str | None = "selling_branch_zip_code",
        file_name: str = "test_file.csv",
    ) -> MagicMock:
        issue = MagicMock()
        issue.id = uuid.uuid4()
        issue.exchange_file_id = uuid.uuid4()
        issue.row_number = 2
        issue.column_name = column_name
        issue.validation_key = validation_key
        issue.message = "Test error message"
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        issue.exchange_file.file_name = file_name
        return issue

    def test_lite_response_includes_file_info(self) -> None:
        """Lite response includes fileId and fileName."""
        issue = self._create_mock_issue(file_name="my_data.csv")

        result = FileValidationIssueLiteResponse.from_model(issue)

        assert result.file_name == "my_data.csv"
        assert str(result.file_id) == str(issue.exchange_file_id)

    def test_lite_response_derives_title(self) -> None:
        """Lite response derives title from validation_key and column_name."""
        issue = self._create_mock_issue(
            validation_key="required_field",
            column_name="selling_branch_zip_code",
        )

        result = FileValidationIssueLiteResponse.from_model(issue)

        assert result.title == "Selling branch zip code missing"


class TestFileValidationIssueLiteResponseNoValidationType:
    @staticmethod
    def _create_mock_issue() -> MagicMock:
        issue = MagicMock()
        issue.id = uuid.uuid4()
        issue.exchange_file_id = uuid.uuid4()
        issue.row_number = 2
        issue.column_name = "selling_branch_zip_code"
        issue.validation_key = "required_field"
        issue.message = "Test error message"
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        issue.exchange_file.file_name = "test_file.csv"
        return issue

    def test_lite_response_does_not_include_validation_type(self) -> None:
        """Lite response does not include validationType (DD-3)."""
        issue = self._create_mock_issue()

        result = FileValidationIssueLiteResponse.from_model(issue)

        assert not hasattr(result, "validation_type")


class TestValidationKeyGroupResponse:
    def test_validation_key_group_has_required_fields(self) -> None:
        """ValidationKeyGroupResponse has validationKey, title, items, count."""
        group = ValidationKeyGroupResponse(
            validation_key="required_field",
            title="Required field missing",
            items=[],
            count=0,
        )

        assert group.validation_key == "required_field"
        assert group.title == "Required field missing"
        assert group.items == []
        assert group.count == 0


class TestFileGroupResponse:
    def test_file_group_has_required_fields(self) -> None:
        """FileGroupResponse has fileId, fileName, items, count, groups."""
        file_group = FileGroupResponse(
            file_id=strawberry.ID("file-1"),
            file_name="sales.csv",
            items=[],
            count=0,
            groups=[],
        )

        assert str(file_group.file_id) == "file-1"
        assert file_group.file_name == "sales.csv"
        assert file_group.items == []
        assert file_group.count == 0
        assert file_group.groups == []

    def test_file_group_contains_key_groups(self) -> None:
        """FileGroupResponse contains ValidationKeyGroupResponse items."""
        key_group = ValidationKeyGroupResponse(
            validation_key="required_field",
            title="Required field missing",
            items=[],
            count=0,
        )
        file_group = FileGroupResponse(
            file_id=strawberry.ID("file-1"),
            file_name="sales.csv",
            items=[],
            count=0,
            groups=[key_group],
        )

        assert len(file_group.groups) == 1
        assert file_group.groups[0].validation_key == "required_field"


class TestValidationIssueGroupResponseWithFiles:
    def test_group_response_includes_files_field(self) -> None:
        """ValidationIssueGroupResponse includes a files field."""
        group = ValidationIssueGroupResponse(
            items=[],
            count=0,
            files=[],
        )

        assert group.files == []

    def test_group_response_with_file_groups(self) -> None:
        """Files field contains FileGroupResponse items."""
        file_group = FileGroupResponse(
            file_id=strawberry.ID("file-1"),
            file_name="sales.csv",
            items=[],
            count=0,
            groups=[],
        )
        group = ValidationIssueGroupResponse(
            items=[],
            count=0,
            files=[file_group],
        )

        assert len(group.files) == 1
        assert group.files[0].file_name == "sales.csv"


class TestFileValidationIssuesResponse:
    def test_grouped_response_structure(self) -> None:
        """Grouped response has blocking, warning, and fyi groups."""
        empty_group = ValidationIssueGroupResponse(items=[], count=0, files=[])
        response = FileValidationIssuesResponse(
            blocking=empty_group,
            warning=empty_group,
            fyi=empty_group,
        )

        assert response.blocking.count == 0
        assert response.warning.count == 0
        assert response.fyi.count == 0
        assert response.blocking.files == []


class TestFilteredFileValidationIssuesQuery:
    @pytest.fixture
    def queries(self) -> FileValidationIssueQueries:
        return FileValidationIssueQueries()

    @staticmethod
    def _create_mock_issue(
        validation_key: str = "required_field",
        column_name: str | None = "selling_branch_zip_code",
        file_name: str = "test_file.csv",
        file_id: uuid.UUID | None = None,
    ) -> MagicMock:
        issue = MagicMock()
        issue.id = uuid.uuid4()
        issue.exchange_file_id = file_id or uuid.uuid4()
        issue.row_number = 2
        issue.column_name = column_name
        issue.validation_key = validation_key
        issue.message = "Test error message"
        issue.row_data = {"field1": "value1"}
        issue.exchange_file = MagicMock()
        issue.exchange_file.id = issue.exchange_file_id
        issue.exchange_file.file_name = file_name
        return issue

    @staticmethod
    async def _call_filtered_issues(
        queries: FileValidationIssueQueries,
        validation_type: ValidationType,
        file_id: strawberry.ID,
        validation_key: str,
        service: AsyncMock,
    ) -> list[FileValidationIssueResponse]:
        unwrapped = queries.filtered_file_validation_issues.__wrapped__
        return await unwrapped(
            queries,
            validation_type=validation_type,
            file_id=file_id,
            validation_key=validation_key,
            service=service,
        )

    @pytest.mark.asyncio
    async def test_returns_list_of_full_responses(
        self, queries: FileValidationIssueQueries
    ) -> None:
        """Returns list of FileValidationIssueResponse with all fields."""
        file_id = uuid.uuid4()
        mock_issues = [
            self._create_mock_issue("required_field", file_id=file_id),
            self._create_mock_issue("required_field", file_id=file_id),
        ]
        mock_service = AsyncMock()
        mock_service.get_filtered_issues.return_value = mock_issues

        result = await self._call_filtered_issues(
            queries,
            validation_type=ValidationType.STANDARD_VALIDATION,
            file_id=strawberry.ID(str(file_id)),
            validation_key="required_field",
            service=mock_service,
        )

        assert len(result) == 2
        assert result[0].validation_key == "required_field"
        assert result[0].message == "Test error message"
        assert result[0].row_data == {"field1": "value1"}

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_results(
        self, queries: FileValidationIssueQueries
    ) -> None:
        """Returns empty list when service returns no issues."""
        mock_service = AsyncMock()
        mock_service.get_filtered_issues.return_value = []

        result = await self._call_filtered_issues(
            queries,
            validation_type=ValidationType.STANDARD_VALIDATION,
            file_id=strawberry.ID(str(uuid.uuid4())),
            validation_key="required_field",
            service=mock_service,
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_passes_parameters_to_service(
        self, queries: FileValidationIssueQueries
    ) -> None:
        """Passes all parameters correctly to the service."""
        file_id = uuid.uuid4()
        mock_service = AsyncMock()
        mock_service.get_filtered_issues.return_value = []

        await self._call_filtered_issues(
            queries,
            validation_type=ValidationType.VALIDATION_WARNING,
            file_id=strawberry.ID(str(file_id)),
            validation_key="lot_order_detection",
            service=mock_service,
        )

        mock_service.get_filtered_issues.assert_called_once_with(
            ValidationType.VALIDATION_WARNING,
            file_id,
            "lot_order_detection",
        )
