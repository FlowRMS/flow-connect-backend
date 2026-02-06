import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.connections.models import ConnectionStatus
from app.graphql.connections.repositories.connection_repository import (
    ConnectionRepository,
)


class TestConnectionRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> ConnectionRepository:
        return ConnectionRepository(session=mock_session)

    @staticmethod
    def _create_mock_connection(
        requester_org_id: uuid.UUID,
        target_org_id: uuid.UUID,
    ) -> MagicMock:
        mock_connection = MagicMock()
        mock_connection.requester_org_id = requester_org_id
        mock_connection.target_org_id = target_org_id
        return mock_connection

    @staticmethod
    def _setup_mock_result(
        mock_session: AsyncMock,
        connections: list[MagicMock],
    ) -> None:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = connections
        mock_session.execute.return_value = mock_result

    @pytest.mark.asyncio
    async def test_get_connected_org_ids_returns_empty_set_when_no_connections(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns empty set when no connections exist."""
        self._setup_mock_result(mock_session, [])

        user_org_id = uuid.uuid4()
        candidate_ids = [uuid.uuid4(), uuid.uuid4()]

        result = await repository.get_connected_org_ids(user_org_id, candidate_ids)

        assert result == set()

    @pytest.mark.asyncio
    async def test_get_connected_org_ids_returns_ids_where_user_is_requester(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns org IDs where user org is the requester."""
        user_org_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()

        mock_connection = self._create_mock_connection(user_org_id, connected_org_id)
        self._setup_mock_result(mock_session, [mock_connection])

        result = await repository.get_connected_org_ids(
            user_org_id, [connected_org_id]
        )

        assert connected_org_id in result

    @pytest.mark.asyncio
    async def test_get_connected_org_ids_returns_ids_where_user_is_target(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns org IDs where user org is the target."""
        user_org_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()

        mock_connection = self._create_mock_connection(connected_org_id, user_org_id)
        self._setup_mock_result(mock_session, [mock_connection])

        result = await repository.get_connected_org_ids(
            user_org_id, [connected_org_id]
        )

        assert connected_org_id in result

    @pytest.mark.asyncio
    async def test_get_connected_org_ids_executes_query_with_filters(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Query is executed with status filter."""
        self._setup_mock_result(mock_session, [])

        user_org_id = uuid.uuid4()
        candidate_ids = [uuid.uuid4()]

        result = await repository.get_connected_org_ids(user_org_id, candidate_ids)

        assert result == set()
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_by_status_returns_count(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns count of connections with the given status."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        result = await repository.count_by_status(org_id, ConnectionStatus.ACCEPTED)

        assert result == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_by_status_returns_zero(
        self,
        repository: ConnectionRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns 0 when no connections with the given status."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        result = await repository.count_by_status(org_id, ConnectionStatus.PENDING)

        assert result == 0
