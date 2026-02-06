import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graphql.pos.field_map.exceptions import (
    CannotDeleteDefaultFieldError,
    CannotEditDefaultFieldError,
    LinkedFieldValidationError,
)
from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_config import DEFAULT_FIELDS
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldMapDirection,
    FieldMapType,
    FieldStatus,
    FieldType,
)
from app.graphql.pos.field_map.services.field_map_service import (
    FieldInput,
    FieldMapService,
)


class TestFieldMapService:
    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_auth_info(self) -> MagicMock:
        auth_info = MagicMock()
        auth_info.flow_user_id = uuid.uuid4()
        return auth_info

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_auth_info: MagicMock,
    ) -> FieldMapService:
        return FieldMapService(
            repository=mock_repository,
            auth_info=mock_auth_info,
        )

    @staticmethod
    def _create_mock_field_map(
        organization_id: uuid.UUID | None = None,
        map_type: FieldMapType = FieldMapType.POS,
        direction: FieldMapDirection = FieldMapDirection.SEND,
        fields: list[MagicMock] | None = None,
    ) -> MagicMock:
        mock_map = MagicMock(spec=FieldMap)
        mock_map.id = uuid.uuid4()
        mock_map.organization_id = organization_id
        mock_map.map_type = map_type.value
        mock_map.direction = direction.value
        mock_map.fields = fields or []
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
        organization_field_name: str | None = None,
        linked: bool = False,
        manufacturer: bool | None = None,
        rep: bool | None = None,
    ) -> MagicMock:
        mock_field = MagicMock(spec=FieldMapField)
        mock_field.id = uuid.uuid4()
        mock_field.field_map_id = field_map_id
        mock_field.standard_field_key = standard_field_key
        mock_field.category = category.value
        mock_field.standard_field_name = standard_field_name
        mock_field.standard_field_name_description = None
        mock_field.organization_field_name = organization_field_name
        mock_field.status = status.value
        mock_field.manufacturer = manufacturer
        mock_field.rep = rep
        mock_field.linked = linked
        mock_field.preferred = False
        mock_field.is_default = is_default
        mock_field.field_type = field_type.value
        mock_field.display_order = 0
        return mock_field

    def _setup_map_with_field(
        self,
        mock_repository: AsyncMock,
        **field_kwargs: object,
    ) -> tuple[uuid.UUID, uuid.UUID, MagicMock, MagicMock]:
        """Create a field map with a single field and configure the repository mock."""
        org_id = uuid.uuid4()
        field_map_id = uuid.uuid4()

        field = self._create_mock_field(field_map_id=field_map_id, **field_kwargs)
        existing_map = self._create_mock_field_map(
            organization_id=org_id,
            fields=[field],
        )
        existing_map.id = field_map_id
        mock_repository.get_by_org_and_type.return_value = existing_map

        return org_id, field_map_id, field, existing_map

    @pytest.mark.asyncio
    async def test_get_or_create_map_creates_new_with_defaults(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Creates map with default fields when not exists."""
        org_id = uuid.uuid4()

        created_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
        )
        # First call returns None (doesn't exist), second call returns the created map
        mock_repository.get_by_org_and_type.side_effect = [None, created_map]
        mock_repository.create.return_value = created_map
        mock_repository.add_fields.return_value = []

        result = await service.get_or_create_map(org_id, FieldMapType.POS)

        mock_repository.create.assert_called_once()
        mock_repository.add_fields.assert_called_once()
        added_fields = mock_repository.add_fields.call_args[0][0]
        assert len(added_fields) == len(DEFAULT_FIELDS)
        assert result == created_map

    @pytest.mark.asyncio
    async def test_get_or_create_map_returns_existing(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Returns existing map without modification."""
        org_id = uuid.uuid4()
        existing_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
        )
        mock_repository.get_by_org_and_type.return_value = existing_map

        result = await service.get_or_create_map(org_id, FieldMapType.POS)

        mock_repository.create.assert_not_called()
        mock_repository.add_fields.assert_not_called()
        assert result == existing_map

    @pytest.mark.asyncio
    async def test_save_fields_updates_existing_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Updates existing field when key matches."""
        org_id, _, existing_field, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="transaction_date",
            is_default=True,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="transaction_date",
                organization_field_name="my_date",
                manufacturer=True,
                rep=True,
            )
        ]

        await service.save_fields(org_id, FieldMapType.POS, field_inputs)

        mock_repository.update_field.assert_called_once()
        assert existing_field.organization_field_name == "my_date"
        assert existing_field.linked is True

    @pytest.mark.asyncio
    async def test_save_fields_adds_new_custom_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Adds new custom field when key not found."""
        org_id = uuid.uuid4()
        field_map_id = uuid.uuid4()

        existing_map = self._create_mock_field_map(
            organization_id=org_id,
            fields=[],
        )
        existing_map.id = field_map_id

        mock_repository.get_by_org_and_type.return_value = existing_map

        field_inputs = [
            FieldInput(
                standard_field_key="custom_field",
                standard_field_name="My Custom Field",
                field_type=FieldType.TEXT,
                category=FieldCategory.CUSTOM_COLUMNS,
            )
        ]

        await service.save_fields(org_id, FieldMapType.POS, field_inputs)

        mock_repository.add_field.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_fields_deletes_missing_custom_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Deletes custom field not in incoming list."""
        org_id = uuid.uuid4()
        field_map_id = uuid.uuid4()

        custom_field = self._create_mock_field(
            field_map_id=field_map_id,
            standard_field_key="old_custom_field",
            is_default=False,
        )
        existing_map = self._create_mock_field_map(
            organization_id=org_id,
            fields=[custom_field],
        )
        existing_map.id = field_map_id

        mock_repository.get_by_org_and_type.return_value = existing_map

        # Empty list means delete all non-default fields
        field_inputs: list[FieldInput] = []

        await service.save_fields(org_id, FieldMapType.POS, field_inputs)

        mock_repository.delete_field.assert_called_once_with(custom_field.id)

    @pytest.mark.asyncio
    async def test_save_fields_cannot_delete_default_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises error when default field is missing from input."""
        org_id, _, _, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="transaction_date",
            is_default=True,
        )

        # Empty list would try to delete default field
        field_inputs: list[FieldInput] = []

        with pytest.raises(CannotDeleteDefaultFieldError):
            await service.save_fields(org_id, FieldMapType.POS, field_inputs)

    @pytest.mark.asyncio
    async def test_cannot_edit_standard_name_of_default_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises error on invalid edit of default field."""
        org_id, _, _, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="transaction_date",
            standard_field_name="Transaction Date",
            is_default=True,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="transaction_date",
                standard_field_name="New Name",  # Cannot edit this for default
            )
        ]

        with pytest.raises(CannotEditDefaultFieldError):
            await service.save_fields(org_id, FieldMapType.POS, field_inputs)

    @pytest.mark.asyncio
    async def test_cannot_edit_field_type_of_default_field(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Raises error when trying to edit field_type of default field."""
        org_id, _, _, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="transaction_date",
            field_type=FieldType.DATE,
            is_default=True,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="transaction_date",
                field_type=FieldType.TEXT,  # Cannot edit this for default
            )
        ]

        with pytest.raises(CannotEditDefaultFieldError):
            await service.save_fields(org_id, FieldMapType.POS, field_inputs)

    @pytest.mark.asyncio
    async def test_linked_auto_calculated_when_org_field_set(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """linked=True when organization_field_name is set."""
        org_id, _, field, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="custom_field",
            is_default=False,
            linked=False,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="custom_field",
                organization_field_name="my_column",
                manufacturer=True,
                rep=True,
            )
        ]

        await service.save_fields(org_id, FieldMapType.POS, field_inputs)

        assert field.linked is True

    @pytest.mark.asyncio
    async def test_linked_false_when_org_field_cleared(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """linked=False when organization_field_name is cleared."""
        org_id, _, field, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="custom_field",
            is_default=False,
            organization_field_name="my_column",
            linked=True,
            manufacturer=True,
            rep=True,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="custom_field",
                organization_field_name=None,  # Clear the mapping
            )
        ]

        await service.save_fields(org_id, FieldMapType.POS, field_inputs)

        assert field.linked is False

    @pytest.mark.asyncio
    async def test_manufacturer_rep_required_when_linked(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Validates manufacturer/rep must be set when linked."""
        org_id, _, _, _ = self._setup_map_with_field(
            mock_repository,
            standard_field_key="custom_field",
            is_default=False,
            manufacturer=None,
            rep=None,
        )

        field_inputs = [
            FieldInput(
                standard_field_key="custom_field",
                organization_field_name="my_column",
                # Missing manufacturer and rep
            )
        ]

        with pytest.raises(LinkedFieldValidationError):
            await service.save_fields(org_id, FieldMapType.POS, field_inputs)

    @pytest.mark.asyncio
    async def test_get_or_create_with_direction(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Creates map with specified direction."""
        org_id = uuid.uuid4()

        created_map = self._create_mock_field_map(
            organization_id=org_id,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.RECEIVE,
        )
        mock_repository.get_by_org_and_type.side_effect = [None, created_map]
        mock_repository.create.return_value = created_map
        mock_repository.add_fields.return_value = []

        result = await service.get_or_create_map(
            org_id, FieldMapType.POS, FieldMapDirection.RECEIVE
        )

        mock_repository.create.assert_called_once()
        created_arg = mock_repository.create.call_args[0][0]
        assert created_arg.direction == FieldMapDirection.RECEIVE.value
        assert result == created_map

    @pytest.mark.asyncio
    async def test_save_preserves_direction(
        self,
        service: FieldMapService,
        mock_repository: AsyncMock,
    ) -> None:
        """Save operation respects direction field."""
        org_id = uuid.uuid4()
        field_map_id = uuid.uuid4()

        existing_map = self._create_mock_field_map(
            organization_id=org_id,
            direction=FieldMapDirection.RECEIVE,
            fields=[],
        )
        existing_map.id = field_map_id
        mock_repository.get_by_org_and_type.return_value = existing_map

        field_inputs: list[FieldInput] = []

        await service.save_fields(
            org_id, FieldMapType.POS, field_inputs, FieldMapDirection.RECEIVE
        )

        # Verify repository was called with correct direction
        mock_repository.get_by_org_and_type.assert_called_with(
            org_id, FieldMapType.POS, FieldMapDirection.RECEIVE
        )
