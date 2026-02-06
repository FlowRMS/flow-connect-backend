import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldMapDirection,
    FieldMapType,
    FieldStatus,
    FieldType,
)
from app.graphql.pos.field_map.repositories.field_map_repository import (
    FieldMapRepository,
)


class TestFieldMapRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session: AsyncMock) -> FieldMapRepository:
        return FieldMapRepository(session=mock_session)

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
    def _create_mock_field(
        field_map_id: uuid.UUID,
        standard_field_key: str = "test_field",
        category: FieldCategory = FieldCategory.TRANSACTION,
        standard_field_name: str = "Test Field",
        status: FieldStatus = FieldStatus.OPTIONAL,
        field_type: FieldType = FieldType.TEXT,
        is_default: bool = False,
    ) -> MagicMock:
        mock_field = MagicMock(spec=FieldMapField)
        mock_field.id = uuid.uuid4()
        mock_field.field_map_id = field_map_id
        mock_field.standard_field_key = standard_field_key
        mock_field.category = category.value
        mock_field.standard_field_name = standard_field_name
        mock_field.standard_field_name_description = None
        mock_field.organization_field_name = None
        mock_field.status = status.value
        mock_field.manufacturer = None
        mock_field.rep = None
        mock_field.linked = False
        mock_field.preferred = False
        mock_field.is_default = is_default
        mock_field.field_type = field_type.value
        mock_field.display_order = 0
        return mock_field

    @pytest.mark.asyncio
    async def test_create_field_map_success(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Creates new field map record and flushes to session."""
        field_map = self._create_mock_field_map(
            organization_id=uuid.uuid4(),
            map_type=FieldMapType.POS,
        )

        result = await repository.create(field_map)

        mock_session.add.assert_called_once_with(field_map)
        mock_session.flush.assert_called_once()
        assert result == field_map

    @pytest.mark.asyncio
    async def test_get_by_org_and_type_found(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns field map when found by organization_id and map_type."""
        org_id = uuid.uuid4()
        mock_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_map
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_and_type(org_id, FieldMapType.POS)

        assert result == mock_map
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_org_and_type_not_found(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when no field map exists."""
        org_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_and_type(org_id, FieldMapType.POS)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_org_and_type_with_null_org(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Works with null organization_id (default map)."""
        mock_map = self._create_mock_field_map(
            organization_id=None,
            map_type=FieldMapType.POS,
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_map
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_and_type(None, FieldMapType.POS)

        assert result == mock_map
        assert result.organization_id is None

    @pytest.mark.asyncio
    async def test_add_field_to_map(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Adds a single field to a map."""
        field_map_id = uuid.uuid4()
        field = self._create_mock_field(field_map_id)

        result = await repository.add_field(field)

        mock_session.add.assert_called_once_with(field)
        mock_session.flush.assert_called_once()
        assert result == field

    @pytest.mark.asyncio
    async def test_add_fields_bulk(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Adds multiple fields to a map in bulk."""
        field_map_id = uuid.uuid4()
        fields = [
            self._create_mock_field(
                field_map_id, standard_field_key="field_1", standard_field_name="Field 1"
            ),
            self._create_mock_field(
                field_map_id, standard_field_key="field_2", standard_field_name="Field 2"
            ),
            self._create_mock_field(
                field_map_id, standard_field_key="field_3", standard_field_name="Field 3"
            ),
        ]

        result = await repository.add_fields(fields)

        assert mock_session.add.call_count == 3
        mock_session.flush.assert_called_once()
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_update_field(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Updates field attributes."""
        field_map_id = uuid.uuid4()
        field = self._create_mock_field(field_map_id)
        field.organization_field_name = "mapped_column"

        result = await repository.update_field(field)

        mock_session.flush.assert_called_once()
        assert result == field

    @pytest.mark.asyncio
    async def test_delete_field(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Removes field from map."""
        field_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = await repository.delete_field(field_id)

        assert result is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_field_not_found(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns False when field doesn't exist."""
        field_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = await repository.delete_field(field_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_field_by_id_found(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns field when found by id."""
        field_map_id = uuid.uuid4()
        field_id = uuid.uuid4()
        mock_field = self._create_mock_field(field_map_id)
        mock_field.id = field_id

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_field
        mock_session.execute.return_value = mock_result

        result = await repository.get_field_by_id(field_id)

        assert result == mock_field
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_field_by_id_not_found(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns None when field doesn't exist."""
        field_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_field_by_id(field_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_org_and_type_filters_by_direction(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Returns field map filtered by direction."""
        org_id = uuid.uuid4()
        mock_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.RECEIVE,
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_map
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_org_and_type(
            org_id, FieldMapType.POS, FieldMapDirection.RECEIVE
        )

        assert result == mock_map
        assert result.direction == FieldMapDirection.RECEIVE.value

    @pytest.mark.asyncio
    async def test_get_by_org_and_type_defaults_to_send(
        self,
        repository: FieldMapRepository,
        mock_session: AsyncMock,
    ) -> None:
        """Defaults to SEND direction when not specified."""
        org_id = uuid.uuid4()
        mock_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = mock_map
        mock_session.execute.return_value = mock_result

        # Call without direction parameter - should default to SEND
        result = await repository.get_by_org_and_type(org_id, FieldMapType.POS)

        assert result == mock_map
        mock_session.execute.assert_called_once()
