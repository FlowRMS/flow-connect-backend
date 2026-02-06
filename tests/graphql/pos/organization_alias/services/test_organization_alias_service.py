import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.models import ConnectionStatus
from app.graphql.pos.organization_alias.exceptions import (
    AliasAlreadyExistsError,
    OrganizationAliasNotFoundError,
    OrganizationNotConnectedError,
)
from app.graphql.pos.organization_alias.models import OrganizationAlias
from app.graphql.pos.organization_alias.services.organization_alias_service import (
    OrganizationAliasService,
)


class TestOrganizationAliasService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
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
    def mock_org_search_repository(self) -> AsyncMock:
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
        mock_connection_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
        mock_org_search_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> OrganizationAliasService:
        return OrganizationAliasService(
            repository=mock_repository,
            connection_repository=mock_connection_repository,
            user_org_repository=mock_user_org_repository,
            org_search_repository=mock_org_search_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_connection(status: ConnectionStatus) -> MagicMock:
        mock_connection = MagicMock()
        mock_connection.status = status.value
        return mock_connection

    @staticmethod
    def _create_mock_alias(
        organization_id: uuid.UUID,
        connected_org_id: uuid.UUID,
        alias: str = "Test Alias",
    ) -> MagicMock:
        mock_alias = MagicMock(spec=OrganizationAlias)
        mock_alias.id = uuid.uuid4()
        mock_alias.organization_id = organization_id
        mock_alias.connected_org_id = connected_org_id
        mock_alias.alias = alias
        return mock_alias

    @pytest.mark.asyncio
    async def test_create_alias_succeeds(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Creates alias for connected org."""
        connected_org_id = uuid.uuid4()
        user_org_id = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )
        mock_repository.alias_exists.return_value = False

        mock_alias = self._create_mock_alias(user_org_id, connected_org_id, "My Alias")
        mock_repository.create.return_value = mock_alias

        result = await service.create_alias(connected_org_id, "My Alias")

        assert result.alias == "My Alias"
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_alias_fails_not_connected(
        self,
        service: OrganizationAliasService,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Raises OrganizationNotConnectedError when connection is not ACCEPTED."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.PENDING)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )

        with pytest.raises(OrganizationNotConnectedError):
            await service.create_alias(connected_org_id, "My Alias")

    @pytest.mark.asyncio
    async def test_create_alias_fails_no_connection(
        self,
        service: OrganizationAliasService,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Raises OrganizationNotConnectedError when no connection exists."""
        connected_org_id = uuid.uuid4()
        mock_connection_repository.get_connection_by_org_id.return_value = None

        with pytest.raises(OrganizationNotConnectedError):
            await service.create_alias(connected_org_id, "My Alias")

    @pytest.mark.asyncio
    async def test_create_alias_fails_duplicate(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
        mock_connection_repository: AsyncMock,
    ) -> None:
        """Raises AliasAlreadyExistsError when alias already exists."""
        connected_org_id = uuid.uuid4()
        mock_connection = self._create_mock_connection(ConnectionStatus.ACCEPTED)
        mock_connection_repository.get_connection_by_org_id.return_value = (
            mock_connection
        )
        mock_repository.alias_exists.return_value = True

        with pytest.raises(AliasAlreadyExistsError):
            await service.create_alias(connected_org_id, "Existing Alias")

    @pytest.mark.asyncio
    async def test_delete_alias_succeeds(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Deletes alias successfully when it belongs to user's org."""
        user_org_id = uuid.uuid4()
        alias_id = uuid.uuid4()

        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        # Alias belongs to the user's organization
        mock_alias = self._create_mock_alias(user_org_id, uuid.uuid4())
        mock_alias.id = alias_id
        mock_repository.get_by_id.return_value = mock_alias
        mock_repository.delete.return_value = True

        result = await service.delete_alias(alias_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(alias_id)

    @pytest.mark.asyncio
    async def test_delete_alias_fails_not_found(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises OrganizationAliasNotFoundError when alias doesn't exist."""
        alias_id = uuid.uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(OrganizationAliasNotFoundError):
            await service.delete_alias(alias_id)

    @pytest.mark.asyncio
    async def test_delete_alias_fails_wrong_organization(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Raises OrganizationAliasNotFoundError when alias belongs to another org."""
        user_org_id = uuid.uuid4()
        other_org_id = uuid.uuid4()
        alias_id = uuid.uuid4()

        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        # Alias belongs to a different organization
        mock_alias = self._create_mock_alias(other_org_id, uuid.uuid4())
        mock_alias.id = alias_id
        mock_repository.get_by_id.return_value = mock_alias

        with pytest.raises(OrganizationAliasNotFoundError):
            await service.delete_alias(alias_id)

    @pytest.mark.asyncio
    async def test_get_all_aliases_grouped(
        self,
        service: OrganizationAliasService,
        mock_repository: AsyncMock,
        mock_user_org_repository: AsyncMock,
    ) -> None:
        """Returns aliases grouped by connected org."""
        user_org_id = uuid.uuid4()
        connected_org_id_1 = uuid.uuid4()
        connected_org_id_2 = uuid.uuid4()
        mock_user_org_repository.get_user_org_id.return_value = user_org_id

        mock_aliases = [
            self._create_mock_alias(user_org_id, connected_org_id_1, "Alias 1"),
            self._create_mock_alias(user_org_id, connected_org_id_2, "Alias 2"),
        ]
        mock_repository.get_all_by_org.return_value = mock_aliases

        result = await service.get_all_aliases_grouped()

        assert len(result) == 2
        mock_repository.get_all_by_org.assert_called_once_with(user_org_id)
