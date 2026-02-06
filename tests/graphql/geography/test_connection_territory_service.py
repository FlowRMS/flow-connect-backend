import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.geography.services.connection_territory_service import (
    ConnectionTerritoryService,
)
from app.graphql.organizations.models import OrgType


class TestConnectionTerritoryService:
    @pytest.fixture
    def mock_territory_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_subdivision_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_org_search_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_connection_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.auth_provider_id = "workos_user_123"
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_territory_repo: AsyncMock,
        mock_subdivision_repo: AsyncMock,
        mock_connection_repo: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> ConnectionTerritoryService:
        return ConnectionTerritoryService(
            territory_repository=mock_territory_repo,
            subdivision_repository=mock_subdivision_repo,
            connection_repository=mock_connection_repo,
            org_search_repository=mock_org_search_repo,
            connection_service=mock_connection_service,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_org(
        org_id: uuid.UUID | None = None,
        org_type: str = "manufacturer",
    ) -> MagicMock:
        mock_org = MagicMock()
        mock_org.id = org_id or uuid.uuid4()
        mock_org.org_type = org_type
        return mock_org

    @staticmethod
    def _create_mock_connection(
        connection_id: uuid.UUID | None = None,
        requester_org_id: uuid.UUID | None = None,
        target_org_id: uuid.UUID | None = None,
    ) -> MagicMock:
        mock_conn = MagicMock()
        mock_conn.id = connection_id or uuid.uuid4()
        mock_conn.requester_org_id = requester_org_id or uuid.uuid4()
        mock_conn.target_org_id = target_org_id or uuid.uuid4()
        return mock_conn

    @staticmethod
    def _create_mock_subdivision(subdivision_id: uuid.UUID | None = None) -> MagicMock:
        mock_sub = MagicMock()
        mock_sub.id = subdivision_id or uuid.uuid4()
        return mock_sub

    # noinspection DuplicatedCode
    # Minor test duplication accepted - shared helper adds complexity without significant benefit
    @pytest.mark.asyncio
    async def test_update_territories_replaces_correctly(
        self,
        service: ConnectionTerritoryService,
        mock_territory_repo: AsyncMock,
        mock_subdivision_repo: AsyncMock,
        mock_connection_repo: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Update territories replaces existing with new ones."""
        user_org_id = uuid.uuid4()
        connection_id = uuid.uuid4()
        subdivision_ids = [uuid.uuid4(), uuid.uuid4()]
        user_org = self._create_mock_org(user_org_id, OrgType.MANUFACTURER.value)
        connection = self._create_mock_connection(
            connection_id, requester_org_id=user_org_id
        )

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_connection_repo.get_by_id.return_value = connection
        mock_subdivision_repo.get_by_ids.return_value = [
            self._create_mock_subdivision(sid) for sid in subdivision_ids
        ]
        mock_territory_repo.set_territories.return_value = []

        await service.update_territories(connection_id, subdivision_ids)

        mock_territory_repo.set_territories.assert_called_once_with(
            connection_id, subdivision_ids
        )

    @pytest.mark.asyncio
    async def test_update_territories_raises_for_non_manufacturer(
        self,
        service: ConnectionTerritoryService,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Non-manufacturers cannot update territories."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, OrgType.DISTRIBUTOR.value)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org

        with pytest.raises(ValueError, match="Only manufacturers can update"):
            await service.update_territories(uuid.uuid4(), [uuid.uuid4()])

    @pytest.mark.asyncio
    async def test_update_territories_raises_for_nonexistent_connection(
        self,
        service: ConnectionTerritoryService,
        mock_connection_repo: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Raises error when connection doesn't exist."""
        user_org_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, OrgType.MANUFACTURER.value)

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_connection_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Connection not found"):
            await service.update_territories(uuid.uuid4(), [uuid.uuid4()])

    # noinspection DuplicatedCode
    # Minor test duplication accepted - shared helper adds complexity without significant benefit
    @pytest.mark.asyncio
    async def test_update_territories_raises_for_invalid_subdivision_ids(
        self,
        service: ConnectionTerritoryService,
        mock_subdivision_repo: AsyncMock,
        mock_connection_repo: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Raises error when subdivision IDs don't exist."""
        user_org_id = uuid.uuid4()
        connection_id = uuid.uuid4()
        subdivision_ids = [uuid.uuid4(), uuid.uuid4()]
        user_org = self._create_mock_org(user_org_id, OrgType.MANUFACTURER.value)
        connection = self._create_mock_connection(
            connection_id, requester_org_id=user_org_id
        )

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_connection_repo.get_by_id.return_value = connection
        # Only return one subdivision instead of two
        mock_subdivision_repo.get_by_ids.return_value = [
            self._create_mock_subdivision(subdivision_ids[0])
        ]

        with pytest.raises(ValueError, match="Invalid subdivision IDs"):
            await service.update_territories(connection_id, subdivision_ids)

    @pytest.mark.asyncio
    async def test_update_territories_raises_for_unauthorized_connection(
        self,
        service: ConnectionTerritoryService,
        mock_connection_repo: AsyncMock,
        mock_org_search_repo: AsyncMock,
        mock_connection_service: AsyncMock,
    ) -> None:
        """Raises error when connection doesn't belong to the caller."""
        user_org_id = uuid.uuid4()
        other_org_id = uuid.uuid4()
        connection_id = uuid.uuid4()
        user_org = self._create_mock_org(user_org_id, OrgType.MANUFACTURER.value)
        # Connection belongs to a different org
        connection = self._create_mock_connection(
            connection_id,
            requester_org_id=other_org_id,
            target_org_id=uuid.uuid4(),
        )

        mock_connection_service.get_user_org_and_connections.return_value = (
            user_org_id,
            set(),
        )
        mock_org_search_repo.get_by_id.return_value = user_org
        mock_connection_repo.get_by_id.return_value = connection

        with pytest.raises(ValueError, match="not authorized"):
            await service.update_territories(connection_id, [uuid.uuid4()])
