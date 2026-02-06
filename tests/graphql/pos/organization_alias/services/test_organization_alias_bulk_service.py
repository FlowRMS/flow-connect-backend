import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.organization_alias.exceptions import (
    AliasAlreadyExistsError,
    OrganizationNotConnectedError,
)
from app.graphql.pos.organization_alias.models import OrganizationAlias
from app.graphql.pos.organization_alias.services.organization_alias_bulk_service import (
    OrganizationAliasBulkService,
)


class TestOrganizationAliasBulkService:
    @pytest.fixture
    def mock_alias_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
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
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_alias_service: AsyncMock,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> OrganizationAliasBulkService:
        return OrganizationAliasBulkService(
            alias_service=mock_alias_service,
            repository=mock_repository,
            user_org_repository=mock_user_org_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_alias(
        connected_org_id: uuid.UUID,
        alias: str,
    ) -> MagicMock:
        mock_alias = MagicMock(spec=OrganizationAlias)
        mock_alias.id = uuid.uuid4()
        mock_alias.connected_org_id = connected_org_id
        mock_alias.alias = alias
        return mock_alias

    @staticmethod
    def _create_csv_content(rows: list[tuple[str, str]]) -> bytes:
        lines = ["Organization Name,Alias"]
        for org_name, alias in rows:
            lines.append(f"{org_name},{alias}")
        return "\n".join(lines).encode("utf-8")

    @pytest.mark.asyncio
    async def test_bulk_create_succeeds(
        self,
        service: OrganizationAliasBulkService,
        mock_alias_service: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Creates multiple aliases successfully."""
        org_id_1 = uuid.uuid4()
        org_id_2 = uuid.uuid4()

        mock_repository.get_connected_orgs_by_name.return_value = {
            "acme corp": MagicMock(id=org_id_1, name="Acme Corp"),
            "beta inc": MagicMock(id=org_id_2, name="Beta Inc"),
        }

        mock_alias_service.create_alias.side_effect = [
            self._create_mock_alias(org_id_1, "Acme"),
            self._create_mock_alias(org_id_2, "Beta"),
        ]

        csv_content = self._create_csv_content([
            ("Acme Corp", "Acme"),
            ("Beta Inc", "Beta"),
        ])

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 2
        assert len(result.failures) == 0

    @pytest.mark.asyncio
    async def test_bulk_create_reports_org_not_found(
        self,
        service: OrganizationAliasBulkService,
        mock_repository: AsyncMock,
    ) -> None:
        """Reports failure when organization not found."""
        mock_repository.get_connected_orgs_by_name.return_value = {}

        csv_content = self._create_csv_content([
            ("Unknown Corp", "Unknown"),
        ])

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 0
        assert len(result.failures) == 1
        assert result.failures[0].reason == "Organization not found"

    @pytest.mark.asyncio
    async def test_bulk_create_reports_not_connected(
        self,
        service: OrganizationAliasBulkService,
        mock_alias_service: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Reports failure when organization not connected."""
        org_id = uuid.uuid4()
        mock_repository.get_connected_orgs_by_name.return_value = {
            "acme corp": MagicMock(id=org_id, name="Acme Corp"),
        }
        mock_alias_service.create_alias.side_effect = OrganizationNotConnectedError(
            "Not connected"
        )

        csv_content = self._create_csv_content([
            ("Acme Corp", "Acme"),
        ])

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 0
        assert len(result.failures) == 1
        assert result.failures[0].reason == "Organization not connected"

    @pytest.mark.asyncio
    async def test_bulk_create_reports_alias_exists(
        self,
        service: OrganizationAliasBulkService,
        mock_alias_service: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Reports failure when alias already exists."""
        org_id = uuid.uuid4()
        mock_repository.get_connected_orgs_by_name.return_value = {
            "acme corp": MagicMock(id=org_id, name="Acme Corp"),
        }
        mock_alias_service.create_alias.side_effect = AliasAlreadyExistsError(
            "Already exists"
        )

        csv_content = self._create_csv_content([
            ("Acme Corp", "Acme"),
        ])

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 0
        assert len(result.failures) == 1
        assert result.failures[0].reason == "Alias already exists"

    @pytest.mark.asyncio
    async def test_bulk_create_reports_missing_alias(
        self,
        service: OrganizationAliasBulkService,
        mock_repository: AsyncMock,
    ) -> None:
        """Reports failure when alias value is missing."""
        org_id = uuid.uuid4()
        mock_repository.get_connected_orgs_by_name.return_value = {
            "acme corp": MagicMock(id=org_id, name="Acme Corp"),
        }

        csv_content = b"Organization Name,Alias\nAcme Corp,"

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 0
        assert len(result.failures) == 1
        assert result.failures[0].reason == "Missing alias value"

    @pytest.mark.asyncio
    async def test_bulk_create_partial_success(
        self,
        service: OrganizationAliasBulkService,
        mock_alias_service: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Some rows succeed, some fail, returns correct counts."""
        org_id_1 = uuid.uuid4()
        org_id_2 = uuid.uuid4()

        mock_repository.get_connected_orgs_by_name.return_value = {
            "acme corp": MagicMock(id=org_id_1, name="Acme Corp"),
            "beta inc": MagicMock(id=org_id_2, name="Beta Inc"),
        }

        mock_alias_service.create_alias.side_effect = [
            self._create_mock_alias(org_id_1, "Acme"),
            AliasAlreadyExistsError("Already exists"),
        ]

        csv_content = self._create_csv_content([
            ("Acme Corp", "Acme"),
            ("Beta Inc", "Beta"),
        ])

        result = await service.bulk_create_from_csv(csv_content)

        assert result.inserted_count == 1
        assert len(result.failures) == 1
        assert result.failures[0].organization_name == "Beta Inc"
