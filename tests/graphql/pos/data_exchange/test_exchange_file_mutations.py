import uuid
from unittest.mock import MagicMock

import strawberry

from app.graphql.pos.data_exchange.strawberry.exchange_file_inputs import (
    UploadExchangeFileInput,
)
from app.graphql.pos.data_exchange.strawberry.exchange_file_types import (
    ExchangeFileLiteResponse,
    ExchangeFileResponse,
    ExchangeFileStatusEnum,
    ExchangeFileTargetOrgResponse,
    PendingFilesStatsResponse,
)


class TestUploadExchangeFileInput:
    def test_input_structure(self) -> None:
        """UploadExchangeFileInput has correct structure."""
        mock_file = MagicMock()
        input_data = UploadExchangeFileInput(
            files=[mock_file],
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[strawberry.ID(str(uuid.uuid4()))],
        )

        assert input_data.reporting_period == "2026-Q1"
        assert input_data.is_pos is True
        assert input_data.is_pot is False
        assert len(input_data.target_org_ids) == 1
        assert len(input_data.files) == 1


class TestExchangeFileStatusEnum:
    def test_enum_values(self) -> None:
        """ExchangeFileStatusEnum has correct values."""
        assert ExchangeFileStatusEnum.PENDING.value == "pending"
        assert ExchangeFileStatusEnum.SENT.value == "sent"


class TestExchangeFileTargetOrgResponse:
    def test_from_model_maps_fields(self) -> None:
        """ExchangeFileTargetOrgResponse.from_model maps fields correctly."""
        target_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.connected_org_id = connected_org_id

        result = ExchangeFileTargetOrgResponse.from_model(mock_target)

        assert str(result.id) == str(target_id)
        assert str(result.connected_org_id) == str(connected_org_id)


class TestExchangeFileLiteResponse:
    # noinspection DuplicatedCode
    # Test isolation: each test has explicit setup for clarity
    def test_from_model_maps_fields(self) -> None:
        """ExchangeFileLiteResponse.from_model maps fields correctly."""
        file_id = uuid.uuid4()
        mock_file = MagicMock()
        mock_file.id = file_id
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.status = "pending"
        mock_file.validation_status = "not_validated"
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False
        mock_file.created_at = None

        result = ExchangeFileLiteResponse.from_model(mock_file)

        assert str(result.id) == str(file_id)
        assert result.file_name == "test.csv"
        assert result.file_size == 1024
        assert result.file_type == "csv"
        assert result.row_count == 100
        assert result.status == ExchangeFileStatusEnum.PENDING
        assert result.reporting_period == "2026-Q1"
        assert result.is_pos is True
        assert result.is_pot is False


class TestExchangeFileResponse:
    # noinspection DuplicatedCode
    # Test isolation: each test has explicit setup for clarity
    def test_from_model_maps_fields_with_targets(self) -> None:
        """ExchangeFileResponse.from_model maps fields including targets."""
        file_id = uuid.uuid4()
        target_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()

        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.connected_org_id = connected_org_id

        mock_file = MagicMock()
        mock_file.id = file_id
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.status = "pending"
        mock_file.validation_status = "not_validated"
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False
        mock_file.created_at = None
        mock_file.target_organizations = [mock_target]

        result = ExchangeFileResponse.from_model(mock_file)

        assert str(result.id) == str(file_id)
        assert len(result.target_organizations) == 1
        assert str(result.target_organizations[0].connected_org_id) == str(
            connected_org_id
        )


class TestPendingFilesStatsResponse:
    def test_response_structure(self) -> None:
        """PendingFilesStatsResponse has correct structure."""
        response = PendingFilesStatsResponse(
            file_count=5,
            total_rows=1500,
        )

        assert response.file_count == 5
        assert response.total_rows == 1500
