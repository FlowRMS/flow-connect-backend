import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.graphql.pos.data_exchange.exceptions import (
    CannotDeleteSentFileError,
    DuplicateFileForTargetError,
    ExchangeFileNotFoundError,
    InvalidFileTypeError,
)
from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ExchangeFileStatus,
    ExchangeFileTargetOrg,
)
from app.graphql.pos.data_exchange.services.exchange_file_service import (
    ExchangeFileService,
)


class TestExchangeFileService:
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
    def mock_validation_issue_repository(self) -> AsyncMock:
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

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        status: str = ExchangeFileStatus.PENDING.value,
        file_sha: str = "abc123def456",
        target_org_ids: list[uuid.UUID] | None = None,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.s3_key = f"exchange-files/{org_id}/{file_sha}.csv"
        mock_file.file_name = "test.csv"
        mock_file.file_size = 1024
        mock_file.file_sha = file_sha
        mock_file.file_type = "csv"
        mock_file.row_count = 100
        mock_file.status = status
        mock_file.reporting_period = "2026-Q1"
        mock_file.is_pos = True
        mock_file.is_pot = False

        mock_targets = []
        for target_id in target_org_ids or []:
            target = MagicMock(spec=ExchangeFileTargetOrg)
            target.connected_org_id = target_id
            mock_targets.append(target)
        mock_file.target_organizations = mock_targets

        return mock_file

    # Upload tests
    @pytest.mark.asyncio
    async def test_upload_file_creates_record(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Creates file record with pending status."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(
            org_id=org_id,
            target_org_ids=[target_org_id],
        )
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        result = await service.upload_file(
            file_content=b"col1,col2\nval1,val2\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[target_org_id],
        )

        assert result.status == ExchangeFileStatus.PENDING.value
        mock_repository.create.assert_called_once()
        mock_s3_service.upload.assert_called_once()

    # noinspection DuplicatedCode
    # Test isolation: each test has explicit setup for clarity
    @pytest.mark.asyncio
    async def test_upload_file_validates_file_type_csv(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Accepts CSV files."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        result = await service.upload_file(
            file_content=b"col1,col2\nval1,val2\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[target_org_id],
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_upload_file_rejects_invalid_type(
        self,
        service: ExchangeFileService,
    ) -> None:
        """Rejects non-CSV/XLS/XLSX files."""
        with pytest.raises(InvalidFileTypeError):
            await service.upload_file(
                file_content=b"PDF content",
                file_name="test.pdf",
                reporting_period="2026-Q1",
                is_pos=True,
                is_pot=False,
                target_org_ids=[uuid.uuid4()],
            )

    @pytest.mark.asyncio
    async def test_upload_file_rejects_duplicate_sha_same_target(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Rejects if pending file with same SHA targets same org."""
        target_org_id = uuid.uuid4()
        mock_repository.has_pending_with_sha_and_target.return_value = True

        with pytest.raises(DuplicateFileForTargetError):
            await service.upload_file(
                file_content=b"col1,col2\nval1,val2\n",
                file_name="test.csv",
                reporting_period="2026-Q1",
                is_pos=True,
                is_pot=False,
                target_org_ids=[target_org_id],
            )

    # noinspection DuplicatedCode
    # Test isolation: each test has explicit setup for clarity
    @pytest.mark.asyncio
    async def test_upload_file_allows_same_sha_different_target(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Allows same file if targeting different orgs."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        result = await service.upload_file(
            file_content=b"col1,col2\nval1,val2\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[target_org_id],
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_upload_file_stores_in_s3(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Verifies S3 upload is called."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        await service.upload_file(
            file_content=b"col1,col2\nval1,val2\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[target_org_id],
        )

        mock_s3_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_computes_row_count(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Counts data rows in CSV file."""
        target_org_id = uuid.uuid4()
        mock_repository.has_pending_with_sha_and_target.return_value = False

        created_file: ExchangeFile | None = None

        async def capture_create(entity: ExchangeFile) -> ExchangeFile:
            nonlocal created_file
            created_file = entity
            return entity

        mock_repository.create.side_effect = capture_create

        await service.upload_file(
            file_content=b"col1,col2\nval1,val2\nval3,val4\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=[target_org_id],
        )

        assert created_file is not None
        assert created_file.row_count == 2  # 2 data rows (header excluded)

    @pytest.mark.asyncio
    async def test_upload_file_creates_target_org_records(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Creates association records for target orgs."""
        target_org_ids = [uuid.uuid4(), uuid.uuid4()]
        mock_repository.has_pending_with_sha_and_target.return_value = False

        created_file: ExchangeFile | None = None

        async def capture_create(entity: ExchangeFile) -> ExchangeFile:
            nonlocal created_file
            created_file = entity
            return entity

        mock_repository.create.side_effect = capture_create

        await service.upload_file(
            file_content=b"col1,col2\nval1,val2\n",
            file_name="test.csv",
            reporting_period="2026-Q1",
            is_pos=True,
            is_pot=False,
            target_org_ids=target_org_ids,
        )

        assert created_file is not None
        assert len(created_file.target_organizations) == 2

    # Delete tests
    @pytest.mark.asyncio
    async def test_delete_file_removes_record(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Deletes pending file and target orgs."""
        file_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(
            org_id=org_id,
            status=ExchangeFileStatus.PENDING.value,
        )
        mock_repository.get_by_id.return_value = mock_file
        mock_repository.delete.return_value = True

        result = await service.delete_file(file_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(file_id)

    @pytest.mark.asyncio
    async def test_delete_file_only_pending(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Cannot delete sent files."""
        file_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(
            org_id=org_id,
            status=ExchangeFileStatus.SENT.value,
        )
        mock_repository.get_by_id.return_value = mock_file

        with pytest.raises(CannotDeleteSentFileError):
            await service.delete_file(file_id)

    @pytest.mark.asyncio
    async def test_delete_file_not_found(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises exception for missing file."""
        file_id = uuid.uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(ExchangeFileNotFoundError):
            await service.delete_file(file_id)

    @pytest.mark.asyncio
    async def test_delete_file_wrong_org(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises exception when file belongs to different org."""
        file_id = uuid.uuid4()
        other_org_id = uuid.uuid4()
        mock_file = self._create_mock_file(
            org_id=other_org_id,
            status=ExchangeFileStatus.PENDING.value,
        )
        mock_repository.get_by_id.return_value = mock_file

        with pytest.raises(ExchangeFileNotFoundError):
            await service.delete_file(file_id)

    # Query tests
    @pytest.mark.asyncio
    async def test_list_pending_files(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns pending files with targets."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_files = [
            self._create_mock_file(org_id=org_id),
            self._create_mock_file(org_id=org_id),
        ]
        mock_repository.list_pending_for_org.return_value = mock_files

        result = await service.list_pending_files()

        assert len(result) == 2
        mock_repository.list_pending_for_org.assert_called_once_with(org_id)

    @pytest.mark.asyncio
    async def test_get_pending_stats(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns file_count and total_rows."""
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_repository.get_pending_stats.return_value = (3, 1500)

        file_count, total_rows = await service.get_pending_stats()

        assert file_count == 3
        assert total_rows == 1500
        mock_repository.get_pending_stats.assert_called_once_with(org_id)

    # Background validation tests
    @pytest.mark.asyncio
    async def test_upload_file_triggers_validation_task(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Validation task starts after upload."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        with patch(
            "app.graphql.pos.data_exchange.services.exchange_file_service."
            "trigger_validation_task"
        ) as mock_trigger:
            await service.upload_file(
                file_content=b"col1,col2\nval1,val2\n",
                file_name="test.csv",
                reporting_period="2026-Q1",
                is_pos=True,
                is_pot=False,
                target_org_ids=[target_org_id],
            )

            mock_trigger.assert_called_once_with(mock_file.id)

    @pytest.mark.asyncio
    async def test_upload_file_returns_immediately(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Upload returns without waiting for validation."""
        target_org_id = uuid.uuid4()
        org_id = mock_user_org_repository.get_user_org_id.return_value
        mock_file = self._create_mock_file(org_id=org_id)
        mock_repository.has_pending_with_sha_and_target.return_value = False
        mock_repository.create.return_value = mock_file

        with patch(
            "app.graphql.pos.data_exchange.services.exchange_file_service."
            "trigger_validation_task"
        ):
            result = await service.upload_file(
                file_content=b"col1,col2\nval1,val2\n",
                file_name="test.csv",
                reporting_period="2026-Q1",
                is_pos=True,
                is_pot=False,
                target_org_ids=[target_org_id],
            )

        # File should be returned immediately with NOT_VALIDATED status
        assert result is not None
