import uuid
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.organizations.repositories import OrganizationSearchRepository
from app.graphql.pos.data_exchange.models import ExchangeFile, ExchangeFileStatus
from app.graphql.pos.data_exchange.repositories.exchange_file_repository import (
    ExchangeFileRepository,
)
from app.graphql.pos.data_exchange.services.exchange_file_service import (
    ExchangeFileService,
)


@dataclass
class MockTargetOrg:
    id: uuid.UUID
    connected_org_id: uuid.UUID


class TestListSentFilesRepository:
    """Tests for ExchangeFileRepository.list_sent_files method."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> ExchangeFileRepository:
        return ExchangeFileRepository(session=mock_session)

    @staticmethod
    def _create_mock_file(
        org_id: uuid.UUID | None = None,
        status: str = ExchangeFileStatus.SENT.value,
        reporting_period: str = "2026-Q1",
        is_pos: bool = True,
        is_pot: bool = False,
        target_org_ids: list[uuid.UUID] | None = None,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.org_id = org_id or uuid.uuid4()
        mock_file.status = status
        mock_file.reporting_period = reporting_period
        mock_file.is_pos = is_pos
        mock_file.is_pot = is_pot
        mock_file.target_organizations = [
            MockTargetOrg(id=uuid.uuid4(), connected_org_id=tid)
            for tid in (target_org_ids or [uuid.uuid4()])
        ]
        return mock_file

    @pytest.mark.asyncio
    async def test_list_sent_files_returns_only_sent_status(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Only returns files with SENT status, excludes PENDING."""
        org_id = uuid.uuid4()
        sent_file = self._create_mock_file(
            org_id=org_id, status=ExchangeFileStatus.SENT.value
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            sent_file
        ]
        mock_session.execute.return_value = mock_result

        result = await repository.list_sent_files(org_id)

        assert len(result) == 1
        assert result[0].status == ExchangeFileStatus.SENT.value

    @pytest.mark.asyncio
    async def test_list_sent_files_filters_by_period(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Filters files by reporting_period when provided."""
        org_id = uuid.uuid4()
        mock_file = self._create_mock_file(org_id=org_id, reporting_period="2026-Q1")

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            mock_file
        ]
        mock_session.execute.return_value = mock_result

        result = await repository.list_sent_files(org_id, period="2026-Q1")

        assert len(result) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_sent_files_filters_by_organizations(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Filters files by target organizations when provided."""
        org_id = uuid.uuid4()
        target_org_id = uuid.uuid4()
        mock_file = self._create_mock_file(
            org_id=org_id, target_org_ids=[target_org_id]
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            mock_file
        ]
        mock_session.execute.return_value = mock_result

        result = await repository.list_sent_files(
            org_id, organizations=[target_org_id]
        )

        assert len(result) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("filter_name", "filter_value"),
        [
            ("is_pos", True),
            ("is_pot", True),
        ],
    )
    async def test_list_sent_files_filters_by_boolean_flag(
        self,
        repository: ExchangeFileRepository,
        mock_session: AsyncMock,
        filter_name: str,
        filter_value: bool,
    ) -> None:
        """Filters files by boolean flag (is_pos/is_pot) when provided."""
        org_id = uuid.uuid4()
        mock_file = self._create_mock_file(org_id=org_id, **{filter_name: filter_value})

        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all.return_value = [
            mock_file
        ]
        mock_session.execute.return_value = mock_result

        result = await repository.list_sent_files(org_id, **{filter_name: filter_value})

        assert len(result) == 1
        mock_session.execute.assert_called_once()


class TestGetSentFilesGroupedService:
    """Tests for ExchangeFileService.get_sent_files_grouped method."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock(spec=ExchangeFileRepository)

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
        return AsyncMock(spec=OrganizationSearchRepository)

    @pytest.fixture
    def mock_validation_issue_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth = MagicMock()
        auth.auth_provider_id = "test-provider-id"
        auth.flow_user_id = uuid.uuid4()
        return auth

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
        reporting_period: str = "2026-Q1",
        target_org_id: uuid.UUID | None = None,
    ) -> MagicMock:
        mock_file = MagicMock(spec=ExchangeFile)
        mock_file.id = uuid.uuid4()
        mock_file.reporting_period = reporting_period
        target_id = target_org_id or uuid.uuid4()
        mock_file.target_organizations = [
            MockTargetOrg(id=uuid.uuid4(), connected_org_id=target_id)
        ]
        return mock_file

    @pytest.mark.asyncio
    async def test_get_sent_files_grouped_by_period(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Groups files by reporting_period."""
        org1 = uuid.uuid4()
        file1 = self._create_mock_file(reporting_period="2026-Q1", target_org_id=org1)
        file2 = self._create_mock_file(reporting_period="2026-Q2", target_org_id=org1)

        mock_repository.list_sent_files.return_value = [file1, file2]
        mock_org_search_repository.get_names_by_ids.return_value = {org1: "Org 1"}

        result = await service.get_sent_files_grouped()

        assert len(result) == 2
        periods = {r.reporting_period for r in result}
        assert periods == {"2026-Q1", "2026-Q2"}

    @pytest.mark.asyncio
    async def test_get_sent_files_grouped_by_organization(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Within a period, groups files by target organization."""
        org1 = uuid.uuid4()
        org2 = uuid.uuid4()
        file1 = self._create_mock_file(reporting_period="2026-Q1", target_org_id=org1)
        file2 = self._create_mock_file(reporting_period="2026-Q1", target_org_id=org2)

        mock_repository.list_sent_files.return_value = [file1, file2]
        mock_org_search_repository.get_names_by_ids.return_value = {
            org1: "Org 1",
            org2: "Org 2",
        }

        result = await service.get_sent_files_grouped()

        assert len(result) == 1
        assert result[0].reporting_period == "2026-Q1"
        assert len(result[0].organizations) == 2

    @pytest.mark.asyncio
    async def test_get_sent_files_includes_org_name(
        self,
        service: ExchangeFileService,
        mock_repository: AsyncMock,
        mock_org_search_repository: AsyncMock,
    ) -> None:
        """Each org group includes the organization name."""
        org1 = uuid.uuid4()
        file1 = self._create_mock_file(reporting_period="2026-Q1", target_org_id=org1)

        mock_repository.list_sent_files.return_value = [file1]
        mock_org_search_repository.get_names_by_ids.return_value = {
            org1: "Test Organization"
        }

        result = await service.get_sent_files_grouped()

        assert len(result) == 1
        assert len(result[0].organizations) == 1
        assert result[0].organizations[0].connected_org_name == "Test Organization"
