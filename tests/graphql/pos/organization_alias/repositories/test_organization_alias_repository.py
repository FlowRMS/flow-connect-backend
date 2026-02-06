import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.organization_alias.models import OrganizationAlias
from app.graphql.pos.organization_alias.repositories.organization_alias_repository import (
    OrganizationAliasRepository,
)


class TestOrganizationAliasRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_orgs_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(
        self,
        mock_session: AsyncMock,
        mock_orgs_session: AsyncMock,
    ) -> OrganizationAliasRepository:
        return OrganizationAliasRepository(
            session=mock_session,
            orgs_session=mock_orgs_session,
        )

    @staticmethod
    def _create_mock_alias(
        organization_id: uuid.UUID | None = None,
        connected_org_id: uuid.UUID | None = None,
        alias: str = "Test Alias",
    ) -> MagicMock:
        mock_alias = MagicMock(spec=OrganizationAlias)
        mock_alias.id = uuid.uuid4()
        mock_alias.organization_id = organization_id or uuid.uuid4()
        mock_alias.connected_org_id = connected_org_id or uuid.uuid4()
        mock_alias.alias = alias
        return mock_alias

    @pytest.mark.asyncio
    async def test_create_alias_returns_alias(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new alias record and flushes to session."""
        alias = self._create_mock_alias()

        result = await repository.create(alias)

        mock_session.add.assert_called_once_with(alias)
        mock_session.flush.assert_called_once()
        assert result == alias

    @pytest.mark.asyncio
    async def test_get_by_id_returns_alias(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns alias when found by id."""
        alias_id = uuid.uuid4()
        mock_alias = self._create_mock_alias()
        mock_alias.id = alias_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_alias
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(alias_id)

        assert result == mock_alias
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when alias doesn't exist."""
        alias_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(alias_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_org_and_connected_org(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns alias when found by organization pair."""
        org_id = uuid.uuid4()
        connected_org_id = uuid.uuid4()
        mock_alias = self._create_mock_alias(
            organization_id=org_id,
            connected_org_id=connected_org_id,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_alias
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_and_connected_org(org_id, connected_org_id)

        assert result == mock_alias
        mock_session.execute.assert_called_once()

    # noinspection DuplicatedCode
    # Minor test duplication accepted - shared helper adds complexity without significant benefit
    @pytest.mark.asyncio
    async def test_get_all_by_org_returns_list(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns all aliases for the user's organization."""
        org_id = uuid.uuid4()
        mock_aliases = [
            self._create_mock_alias(organization_id=org_id, alias="Alias 1"),
            self._create_mock_alias(organization_id=org_id, alias="Alias 2"),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_aliases
        mock_session.execute.return_value = mock_result

        result = await repository.get_all_by_org(org_id)

        assert len(result) == 2
        assert result == mock_aliases
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_alias_exists_case_insensitive_returns_true(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns True when alias exists (case-insensitive check)."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        mock_session.execute.return_value = mock_result

        result = await repository.alias_exists(org_id, "Test Alias")

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_alias_exists_returns_false_when_not_found(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when alias doesn't exist."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.alias_exists(org_id, "Nonexistent Alias")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_removes_alias(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Deletes alias and returns True."""
        alias_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(alias_id)

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(
        self,
        repository: OrganizationAliasRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when alias doesn't exist."""
        alias_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(alias_id)

        assert result is False
