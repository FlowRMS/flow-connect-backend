import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.agreement.models.agreement import Agreement
from app.graphql.pos.agreement.repositories.agreement_repository import (
    AgreementRepository,
)


class TestAgreementRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> AgreementRepository:
        return AgreementRepository(session=mock_session)

    @staticmethod
    def _create_mock_agreement(
        connected_org_id: uuid.UUID,
        s3_key: str = "agreements/test/file.pdf",
        file_name: str = "file.pdf",
        file_size: int = 1024,
        file_sha: str = "abc123",
    ) -> MagicMock:
        mock_agreement = MagicMock(spec=Agreement)
        mock_agreement.id = uuid.uuid4()
        mock_agreement.connected_org_id = connected_org_id
        mock_agreement.s3_key = s3_key
        mock_agreement.file_name = file_name
        mock_agreement.file_size = file_size
        mock_agreement.file_sha = file_sha
        return mock_agreement

    @pytest.mark.asyncio
    async def test_create_agreement_success(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new agreement record and flushes to session."""
        connected_org_id = uuid.uuid4()
        agreement = self._create_mock_agreement(connected_org_id)

        result = await repository.create(agreement)

        mock_session.add.assert_called_once_with(agreement)
        mock_session.flush.assert_called_once()
        assert result == agreement

    @pytest.mark.asyncio
    async def test_get_by_connected_org_id_found(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns agreement when found by connected_org_id."""
        connected_org_id = uuid.uuid4()
        mock_agreement = self._create_mock_agreement(connected_org_id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_agreement
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_connected_org_id(connected_org_id)

        assert result == mock_agreement
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_connected_org_id_not_found(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when no agreement exists for connected_org_id."""
        connected_org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_connected_org_id(connected_org_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_upsert_creates_when_not_exists(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Upsert creates new record when agreement doesn't exist."""
        connected_org_id = uuid.uuid4()
        agreement = self._create_mock_agreement(connected_org_id)

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = agreement
        mock_session.execute.return_value = mock_result

        result = await repository.upsert(agreement)

        assert result.connected_org_id == connected_org_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_updates_when_exists(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Upsert updates existing record when agreement exists."""
        connected_org_id = uuid.uuid4()
        agreement = self._create_mock_agreement(
            connected_org_id,
            s3_key="agreements/test/new_file.pdf",
            file_name="new_file.pdf",
        )

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = agreement
        mock_session.execute.return_value = mock_result

        result = await repository.upsert(agreement)

        assert result.file_name == "new_file.pdf"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_existing_agreement(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete returns True when agreement exists and is deleted."""
        connected_org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(connected_org_id)

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(
        self,
        repository: AgreementRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Delete returns False when no agreement exists."""
        connected_org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(connected_org_id)

        assert result is False
