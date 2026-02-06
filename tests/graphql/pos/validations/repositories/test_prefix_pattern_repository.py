import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.validations.models import PrefixPattern
from app.graphql.pos.validations.repositories.prefix_pattern_repository import (
    PrefixPatternRepository,
)


class TestPrefixPatternRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> PrefixPatternRepository:
        return PrefixPatternRepository(session=mock_session)

    @staticmethod
    def _create_mock_pattern(
        organization_id: uuid.UUID | None = None,
        name: str = "Test Pattern",
        description: str | None = "Test Description",
    ) -> MagicMock:
        mock_pattern = MagicMock(spec=PrefixPattern)
        mock_pattern.id = uuid.uuid4()
        mock_pattern.organization_id = organization_id or uuid.uuid4()
        mock_pattern.name = name
        mock_pattern.description = description
        return mock_pattern

    @pytest.mark.asyncio
    async def test_create_prefix_pattern(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new pattern record and flushes to session."""
        pattern = self._create_mock_pattern()

        result = await repository.create(pattern)

        mock_session.add.assert_called_once_with(pattern)
        mock_session.flush.assert_called_once()
        assert result == pattern

    @pytest.mark.asyncio
    async def test_get_by_id_returns_pattern(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns pattern when found by id."""
        pattern_id = uuid.uuid4()
        mock_pattern = self._create_mock_pattern()
        mock_pattern.id = pattern_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_pattern
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(pattern_id)

        assert result == mock_pattern
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_when_not_found(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when pattern doesn't exist."""
        pattern_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_id(pattern_id)

        assert result is None

    # noinspection DuplicatedCode
    # Minor test duplication accepted - shared helper adds complexity without significant benefit
    @pytest.mark.asyncio
    async def test_get_all_by_org_returns_patterns(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns all patterns for the organization."""
        org_id = uuid.uuid4()
        mock_patterns = [
            self._create_mock_pattern(organization_id=org_id, name="Pattern 1"),
            self._create_mock_pattern(organization_id=org_id, name="Pattern 2"),
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_patterns
        mock_session.execute.return_value = mock_result

        result = await repository.get_all_by_org(org_id)

        assert len(result) == 2
        assert result == mock_patterns
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_removes_pattern(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Deletes pattern and returns True."""
        pattern_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete(pattern_id)

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when pattern doesn't exist."""
        pattern_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete(pattern_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_by_org_and_name_returns_true(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns True when pattern with name exists in organization."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 1
        mock_session.execute.return_value = mock_result

        result = await repository.exists_by_org_and_name(org_id, "Test Pattern")

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_by_org_and_name_returns_false(
        self,
        repository: PrefixPatternRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when pattern doesn't exist."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.exists_by_org_and_name(org_id, "Nonexistent")

        assert result is False
