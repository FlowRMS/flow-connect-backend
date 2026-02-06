import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
import strawberry

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_config import DEFAULT_FIELDS
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)
from app.graphql.pos.field_map.queries.field_map_queries import FieldMapQueries


class TestFieldMapQueries:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def queries(self) -> FieldMapQueries:
        return FieldMapQueries()

    @staticmethod
    def _create_mock_field_map(
        organization_id: uuid.UUID | None = None,
        map_type: FieldMapType = FieldMapType.POS,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> MagicMock:
        mock_map = MagicMock(spec=FieldMap)
        mock_map.id = uuid.uuid4()
        mock_map.organization_id = organization_id
        mock_map.map_type = map_type.value
        mock_map.direction = direction.value
        mock_map.fields = []
        return mock_map

    @staticmethod
    async def _call_field_map(
        queries: FieldMapQueries,
        repository: AsyncMock,
        map_type: FieldMapType,
        organization_id: strawberry.ID | None = None,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ):
        """Call the field_map method bypassing the aioinject decorator."""
        # Access the underlying method via __wrapped__ to bypass decorators
        unwrapped = queries.field_map.__wrapped__
        return await unwrapped(
            queries,
            map_type=map_type,
            repository=repository,
            organization_id=organization_id,
            direction=direction,
        )

    @pytest.mark.asyncio
    async def test_returns_virtual_defaults_when_not_found(
        self,
        queries: FieldMapQueries,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns virtual defaults with id=None when no DB record exists."""
        mock_repository.get_by_org_and_type.return_value = None

        result = await self._call_field_map(
            queries=queries,
            repository=mock_repository,
            map_type=FieldMapType.POS,
            organization_id=None,
            direction=FieldMapDirection.SEND,
        )

        assert result is not None
        assert result.id is None
        assert len(result.fields) == len(DEFAULT_FIELDS)

    @pytest.mark.asyncio
    async def test_returns_db_record_when_exists(
        self,
        queries: FieldMapQueries,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns actual record with real ID when exists in DB."""
        existing_map = self._create_mock_field_map()
        mock_repository.get_by_org_and_type.return_value = existing_map

        result = await self._call_field_map(
            queries=queries,
            repository=mock_repository,
            map_type=FieldMapType.POS,
            organization_id=None,
            direction=FieldMapDirection.SEND,
        )

        assert result is not None
        assert result.id == strawberry.ID(str(existing_map.id))

    @pytest.mark.asyncio
    async def test_virtual_defaults_for_pot(
        self,
        queries: FieldMapQueries,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns virtual defaults for POT map type."""
        mock_repository.get_by_org_and_type.return_value = None

        result = await self._call_field_map(
            queries=queries,
            repository=mock_repository,
            map_type=FieldMapType.POT,
            organization_id=None,
            direction=FieldMapDirection.SEND,
        )

        assert result is not None
        assert result.id is None
        assert result.map_type == FieldMapType.POT

    @pytest.mark.asyncio
    async def test_virtual_defaults_for_receive_direction(
        self,
        queries: FieldMapQueries,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns virtual defaults for RECEIVE direction."""
        mock_repository.get_by_org_and_type.return_value = None

        result = await self._call_field_map(
            queries=queries,
            repository=mock_repository,
            map_type=FieldMapType.POS,
            organization_id=None,
            direction=FieldMapDirection.RECEIVE,
        )

        assert result is not None
        assert result.id is None
        assert result.direction == FieldMapDirection.RECEIVE

    @pytest.mark.asyncio
    async def test_virtual_defaults_with_organization_id(
        self,
        queries: FieldMapQueries,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns virtual defaults with correct organization_id."""
        org_id = uuid.uuid4()
        mock_repository.get_by_org_and_type.return_value = None

        result = await self._call_field_map(
            queries=queries,
            repository=mock_repository,
            map_type=FieldMapType.POS,
            organization_id=strawberry.ID(str(org_id)),
            direction=FieldMapDirection.SEND,
        )

        assert result is not None
        assert result.id is None
        assert result.organization_id == strawberry.ID(str(org_id))
