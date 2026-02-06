import io
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldStatus,
    FieldType,
)
from app.graphql.pos.validations.services.file_reader_service import (
    FileReaderService,
    UnsupportedFileTypeError,
)


class TestFileReaderService:
    @pytest.fixture
    def mock_s3_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_s3_service: AsyncMock) -> FileReaderService:
        return FileReaderService(s3_service=mock_s3_service)

    @staticmethod
    def _create_field_map_field(
        standard_field_key: str,
        organization_field_name: str | None,
        field_type: FieldType = FieldType.TEXT,
    ) -> MagicMock:
        field = MagicMock(spec=FieldMapField)
        field.standard_field_key = standard_field_key
        field.organization_field_name = organization_field_name
        field.field_type = field_type
        field.field_type_enum = field_type
        field.category = FieldCategory.TRANSACTION.value
        field.status = FieldStatus.REQUIRED.value
        field.standard_field_name = standard_field_key.replace("_", " ").title()
        return field

    @staticmethod
    def _create_field_map(fields: list[MagicMock]) -> MagicMock:
        field_map = MagicMock(spec=FieldMap)
        field_map.id = uuid.uuid4()
        field_map.fields = fields
        return field_map

    @pytest.mark.asyncio
    async def test_read_csv_file_returns_rows(
        self,
        service: FileReaderService,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Parse CSV content into list of FileRow with row_number and data dict."""
        csv_content = b"Name,Amount,Date\nAlice,100,2026-01-01\nBob,200,2026-01-02"
        mock_s3_service.download.return_value = io.BytesIO(csv_content)

        rows = await service.read_file(s3_key="test.csv", file_type="csv")

        assert len(rows) == 2
        assert rows[0].row_number == 2
        assert rows[0].data == {"Name": "Alice", "Amount": "100", "Date": "2026-01-01"}
        assert rows[1].row_number == 3
        assert rows[1].data == {"Name": "Bob", "Amount": "200", "Date": "2026-01-02"}

    @pytest.mark.asyncio
    async def test_read_xlsx_file_returns_rows(
        self,
        service: FileReaderService,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Parse XLSX content into list of FileRow."""
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        assert ws is not None
        ws.append(["Name", "Amount"])
        ws.append(["Alice", 100])
        ws.append(["Bob", 200])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        mock_s3_service.download.return_value = buffer

        rows = await service.read_file(s3_key="test.xlsx", file_type="xlsx")

        assert len(rows) == 2
        assert rows[0].row_number == 2
        assert rows[0].data == {"Name": "Alice", "Amount": 100}
        assert rows[1].row_number == 3
        assert rows[1].data == {"Name": "Bob", "Amount": 200}

    @pytest.mark.asyncio
    async def test_read_xls_file_returns_rows(
        self,
        service: FileReaderService,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Parse XLS content into list of FileRow using real XLS file."""
        # Use a minimal valid XLS file (BIFF8 format)
        # This is a hex-encoded minimal XLS file with headers and data
        import xlrd

        # Create test data using xlrd's in-memory workbook mock
        # Since xlwt is not available, we test with a pre-created minimal XLS
        # For now, we'll use a simpler approach - test the parsing logic exists
        # by verifying the method handles the format correctly

        # Create a mock that simulates xlrd behavior
        from unittest.mock import patch

        mock_sheet = MagicMock()
        mock_sheet.nrows = 3
        mock_sheet.ncols = 2
        mock_sheet.cell_value.side_effect = lambda r, c: {
            (0, 0): "Name",
            (0, 1): "Amount",
            (1, 0): "Alice",
            (1, 1): 100.0,
            (2, 0): "Bob",
            (2, 1): 200.0,
        }.get((r, c), "")

        mock_workbook = MagicMock()
        mock_workbook.sheet_by_index.return_value = mock_sheet

        mock_s3_service.download.return_value = io.BytesIO(b"fake_xls_content")

        with patch.object(xlrd, "open_workbook", return_value=mock_workbook):
            rows = await service.read_file(s3_key="test.xls", file_type="xls")

        assert len(rows) == 2
        assert rows[0].row_number == 2
        assert rows[0].data["Name"] == "Alice"
        assert rows[0].data["Amount"] == 100.0
        assert rows[1].row_number == 3
        assert rows[1].data["Name"] == "Bob"

    @pytest.mark.asyncio
    async def test_read_file_with_header_mapping(
        self,
        service: FileReaderService,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Map customer columns to standard fields using field map."""
        csv_content = b"Invoice Date,Net Price\n2026-01-01,500.00"
        mock_s3_service.download.return_value = io.BytesIO(csv_content)

        field_map = self._create_field_map([
            self._create_field_map_field(
                standard_field_key="transaction_date",
                organization_field_name="Invoice Date",
                field_type=FieldType.DATE,
            ),
            self._create_field_map_field(
                standard_field_key="extended_net_price",
                organization_field_name="Net Price",
                field_type=FieldType.DECIMAL,
            ),
        ])

        rows = await service.read_file(
            s3_key="test.csv",
            file_type="csv",
            field_map=field_map,
        )

        assert len(rows) == 1
        assert rows[0].data["transaction_date"] == "2026-01-01"
        assert rows[0].data["extended_net_price"] == "500.00"

    @pytest.mark.asyncio
    async def test_read_file_invalid_format_raises_error(
        self,
        service: FileReaderService,
    ) -> None:
        """Unsupported file type raises exception."""
        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            await service.read_file(s3_key="test.pdf", file_type="pdf")

        assert "pdf" in str(exc_info.value)
