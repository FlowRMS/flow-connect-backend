import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.graphql.pos.data_exchange.models import ExchangeFile, ValidationStatus
from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validation_execution_service import (
    ValidationExecutionService,
)
from app.graphql.pos.validations.services.validators.base import ValidationIssue


class TestValidationExecutionService:
    @pytest.fixture
    def mock_exchange_file_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_file_reader_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_validation_issue_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_field_map_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(
        self,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
        mock_field_map_repository: AsyncMock,
    ) -> ValidationExecutionService:
        return ValidationExecutionService(
            exchange_file_repository=mock_exchange_file_repository,
            file_reader_service=mock_file_reader_service,
            validation_issue_repository=mock_validation_issue_repository,
            field_map_repository=mock_field_map_repository,
        )

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        status: str = "pending",
        validation_status: str = "not_validated",
        is_pos: bool = True,
        is_pot: bool = False,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.s3_key = "test/path/file.csv"
        mock_file.file_type = "csv"
        mock_file.status = status
        mock_file.validation_status = validation_status
        mock_file.is_pos = is_pos
        mock_file.is_pot = is_pot
        return mock_file

    @staticmethod
    def _create_mock_field_map() -> MagicMock:
        field_map = MagicMock(spec=FieldMap)
        field_map.id = uuid.uuid4()
        field_map.fields = []
        return field_map

    @pytest.mark.asyncio
    async def test_validate_file_updates_status_to_validating(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Status changes to VALIDATING at start, then to final status."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = []

        statuses_seen: list[str] = []

        def capture_status(f: MagicMock) -> MagicMock:
            statuses_seen.append(f.validation_status)
            return f

        mock_exchange_file_repository.update.side_effect = capture_status

        await service.validate_file(file.id)

        assert ValidationStatus.VALIDATING.value in statuses_seen
        assert mock_exchange_file_repository.update.call_count >= 2

    @pytest.mark.asyncio
    async def test_validate_file_with_errors_sets_invalid(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Blocking errors set INVALID."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()
        rows = [FileRow(row_number=2, data={"field": "value"})]

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = rows

        blocking_issue = ValidationIssue(
            row_number=2,
            column_name="field",
            validation_key="required_field",
            message="Error",
        )

        with patch.object(
            service, "_run_validation", return_value=([blocking_issue], True)
        ):
            await service.validate_file(file.id)

        assert file.validation_status == ValidationStatus.INVALID.value

    @pytest.mark.asyncio
    async def test_validate_file_success_sets_valid(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """No blocking errors set VALID."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = []

        with patch.object(service, "_run_validation", return_value=([], False)):
            await service.validate_file(file.id)

        assert file.validation_status == ValidationStatus.VALID.value

    @pytest.mark.asyncio
    async def test_validate_file_stores_issues(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Issues persisted to database."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = []

        issues = [
            ValidationIssue(
                row_number=2,
                column_name="field",
                validation_key="required_field",
                message="Error",
            )
        ]

        with patch.object(service, "_run_validation", return_value=(issues, True)):
            await service.validate_file(file.id)

        mock_validation_issue_repository.create_bulk.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_file_clears_previous_issues(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Re-validation clears old issues."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = []

        await service.validate_file(file.id)

        mock_validation_issue_repository.delete_by_file_id.assert_called_once_with(
            file.id
        )

    @pytest.mark.asyncio
    async def test_validation_issue_includes_row_data(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Issue created with row_data populated containing all columns."""
        file = self._create_mock_file()
        field_map = self._create_mock_field_map()
        row_data = {
            "invoice_number": "INV-001",
            "product_id": "ABC123",
            "quantity": 10,
            "unit_price": 9.99,
            "extended_price": 99.90,
        }

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = [
            FileRow(row_number=2, data=row_data)
        ]

        issue = ValidationIssue(
            row_number=2,
            column_name="product_id",
            validation_key="required_field",
            message="Error",
            row_data=row_data,
        )

        with patch.object(service, "_run_validation", return_value=([issue], True)):
            await service.validate_file(file.id)

        mock_validation_issue_repository.create_bulk.assert_called_once()
        created_issues = mock_validation_issue_repository.create_bulk.call_args[0][0]
        assert len(created_issues) == 1
        assert created_issues[0].row_data == row_data

    @pytest.mark.asyncio
    async def test_validation_uses_send_direction_map(
        self,
        service: ValidationExecutionService,
        mock_exchange_file_repository: AsyncMock,
        mock_file_reader_service: AsyncMock,
        mock_field_map_repository: AsyncMock,
        mock_validation_issue_repository: AsyncMock,
    ) -> None:
        """Validation explicitly requests SEND direction maps."""
        file = self._create_mock_file(is_pos=True, is_pot=False)
        field_map = self._create_mock_field_map()

        mock_exchange_file_repository.get_by_id.return_value = file
        mock_field_map_repository.get_by_org_and_type.return_value = field_map
        mock_file_reader_service.read_file.return_value = []

        with patch.object(service, "_run_validation", return_value=([], False)):
            await service.validate_file(file.id)

        # Verify repository was called with explicit SEND direction
        mock_field_map_repository.get_by_org_and_type.assert_called_with(
            file.org_id, FieldMapType.POS, FieldMapDirection.SEND
        )
