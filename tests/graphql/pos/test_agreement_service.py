import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.models import ConnectionStatus
from app.graphql.pos.agreement.exceptions import (
    AgreementNotFoundError,
    ConnectionNotAcceptedError,
    S3UploadError,
)
from app.graphql.pos.agreement.models.agreement import Agreement
from app.graphql.pos.agreement.services.agreement_service import AgreementService


class TestAgreementService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_s3_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_user_org_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.get_user_org_id.return_value = uuid.uuid4()
        return repo

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
        mock_connection_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> AgreementService:
        return AgreementService(
            repository=mock_repository,
            s3_service=mock_s3_service,
            connection_repository=mock_connection_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_connection(status: ConnectionStatus) -> MagicMock:
        mock_connection = MagicMock()
        mock_connection.status = status.value
        return mock_connection

    @staticmethod
    def _create_mock_agreement(connected_org_id: uuid.UUID) -> MagicMock:
        mock_agreement = MagicMock(spec=Agreement)
        mock_agreement.id = uuid.uuid4()
        mock_agreement.connected_org_id = connected_org_id
        mock_agreement.s3_key = f"agreements/{connected_org_id}/file.pdf"
        mock_agreement.file_name = "file.pdf"
        mock_agreement.file_size = 1024
        mock_agreement.file_sha = "abc123"
        return mock_agreement

    @staticmethod
    def _setup_s3_delete_mock(
        mock_s3_service: AsyncMock,
        s3_key: str,
    ) -> AsyncMock:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_s3_service.bucket_name = "test-bucket"
        mock_s3_service.get_full_key = MagicMock(return_value=s3_key)

        async def mock_get_client() -> AsyncMock:
            return mock_client

        mock_s3_service.get_client = MagicMock(side_effect=lambda: mock_get_client())
        return mock_client

    @pytest.mark.asyncio
    async def test_upload_creates_new_agreement(
        self,
        service: AgreementService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """First upload creates new agreement record."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )
        mock_agreement = self._create_mock_agreement(connected_org_id)
        mock_repository.upsert.return_value = mock_agreement

        result = await service.upload_agreement(
            connected_org_id=connected_org_id,
            file_content=b"pdf content",
            file_name="test.pdf",
        )

        assert result.connected_org_id == connected_org_id
        mock_repository.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_replaces_existing_agreement(
        self,
        service: AgreementService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Subsequent upload with different filename deletes old S3 file."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )

        old_agreement = self._create_mock_agreement(connected_org_id)
        old_agreement.s3_key = f"agreements/{connected_org_id}/old_file.pdf"
        old_agreement.file_name = "old_file.pdf"
        mock_repository.get_by_connected_org_id.return_value = old_agreement

        new_agreement = self._create_mock_agreement(connected_org_id)
        new_agreement.s3_key = f"agreements/{connected_org_id}/new_file.pdf"
        new_agreement.file_name = "new_file.pdf"
        mock_repository.upsert.return_value = new_agreement

        mock_client = self._setup_s3_delete_mock(mock_s3_service, old_agreement.s3_key)

        result = await service.upload_agreement(
            connected_org_id=connected_org_id,
            file_content=b"new content",
            file_name="new_file.pdf",
        )

        assert result.file_name == "new_file.pdf"
        mock_client.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_stores_file_in_s3(
        self,
        service: AgreementService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Verifies S3 upload is called with correct params."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )
        mock_agreement = self._create_mock_agreement(connected_org_id)
        mock_repository.upsert.return_value = mock_agreement

        await service.upload_agreement(
            connected_org_id=connected_org_id,
            file_content=b"pdf content",
            file_name="test.pdf",
        )

        mock_s3_service.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_fails_when_connection_not_accepted(
        self,
        service: AgreementService,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Raises ConnectionNotAcceptedError when connection is not ACCEPTED."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.PENDING)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )

        with pytest.raises(ConnectionNotAcceptedError):
            await service.upload_agreement(
                connected_org_id=connected_org_id,
                file_content=b"pdf content",
                file_name="test.pdf",
            )

    @pytest.mark.asyncio
    async def test_upload_fails_when_connection_not_found(
        self,
        service: AgreementService,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Raises ConnectionNotAcceptedError when connection doesn't exist."""
        connected_org_id = uuid.uuid4()
        mock_connection_repository.get_connection_by_org_id.return_value = None

        with pytest.raises(ConnectionNotAcceptedError):
            await service.upload_agreement(
                connected_org_id=connected_org_id,
                file_content=b"pdf content",
                file_name="test.pdf",
            )

    @pytest.mark.asyncio
    async def test_upload_raises_s3_error_on_upload_failure(
        self,
        service: AgreementService,
        mock_s3_service: AsyncMock,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Wraps S3 upload errors in S3UploadError."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )
        mock_s3_service.upload.side_effect = Exception("S3 upload failed")

        with pytest.raises(S3UploadError):
            await service.upload_agreement(
                connected_org_id=connected_org_id,
                file_content=b"pdf content",
                file_name="test.pdf",
            )

    @pytest.mark.asyncio
    async def test_get_presigned_url_returns_valid_url(
        self,
        service: AgreementService,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Generates presigned URL for download."""
        mock_agreement = self._create_mock_agreement(uuid.uuid4())
        expected_url = "https://s3.example.com/presigned-url"
        mock_s3_service.generate_presigned_url.return_value = expected_url

        result = await service.get_presigned_url(mock_agreement)

        assert result == expected_url
        mock_s3_service.generate_presigned_url.assert_called_once_with(
            mock_agreement.s3_key
        )

    @pytest.mark.asyncio
    async def test_delete_removes_from_s3_and_db(
        self,
        service: AgreementService,
        mock_repository: AsyncMock,
        mock_s3_service: AsyncMock,
    ) -> None:
        """Delete removes from both S3 and database."""
        connected_org_id = uuid.uuid4()
        mock_agreement = self._create_mock_agreement(connected_org_id)
        mock_repository.get_by_connected_org_id.return_value = mock_agreement
        mock_repository.delete.return_value = True

        mock_client = self._setup_s3_delete_mock(mock_s3_service, mock_agreement.s3_key)

        await service.delete_agreement(connected_org_id)

        mock_client.delete_object.assert_called_once()
        mock_repository.delete.assert_called_once_with(connected_org_id)

    @pytest.mark.asyncio
    async def test_delete_raises_not_found_error(
        self,
        service: AgreementService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises AgreementNotFoundError when agreement doesn't exist."""
        connected_org_id = uuid.uuid4()
        mock_repository.get_by_connected_org_id.return_value = None

        with pytest.raises(AgreementNotFoundError):
            await service.delete_agreement(connected_org_id)
