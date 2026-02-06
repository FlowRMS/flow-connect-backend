import uuid
from dataclasses import dataclass

from commons.auth import AuthInfo

from app.graphql.pos.field_map.exceptions import (
    CannotDeleteDefaultFieldError,
    CannotEditDefaultFieldError,
    LinkedFieldValidationError,
)
from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_config import (
    DEFAULT_FIELD_KEYS,
    DEFAULT_FIELDS,
    generate_unique_field_key,
    get_default_field_by_key,
)
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


# noinspection DuplicatedCode
# Intentional code duplication - Service layer uses dataclass, GraphQL layer uses strawberry.input (separation of concerns)
@dataclass
class FieldInput:
    """Input for a field in the save operation."""

    standard_field_key: str
    organization_field_name: str | None = None
    manufacturer: bool | None = None
    rep: bool | None = None
    # Only for custom fields (non-default)
    standard_field_name: str | None = None
    field_type: FieldType | None = None
    category: FieldCategory | None = None
    status: FieldStatus | None = None


class FieldMapService:
    def __init__(
        self,
        repository: FieldMapRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def get_field_map(
        self,
        organization_id: uuid.UUID | None,
        map_type: FieldMapType,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> FieldMap | None:
        return await self.repository.get_by_org_and_type(
            organization_id, map_type, direction
        )

    async def get_or_create_map(
        self,
        organization_id: uuid.UUID | None,
        map_type: FieldMapType,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> FieldMap:
        existing = await self.repository.get_by_org_and_type(
            organization_id, map_type, direction
        )
        if existing:
            return existing

        field_map = FieldMap(
            map_type=map_type.value,
            direction=direction.value,
            organization_id=organization_id,
        )
        field_map.created_by_id = self.auth_info.flow_user_id
        created_map = await self.repository.create(field_map)

        default_fields = self._create_default_fields(created_map.id)
        await self.repository.add_fields(default_fields)

        # Re-fetch to get fields loaded via joined load
        loaded_map = await self.repository.get_by_org_and_type(
            organization_id, map_type, direction
        )
        if not loaded_map:
            raise RuntimeError("Field map not found after creation")
        return loaded_map

    async def save_fields(
        self,
        organization_id: uuid.UUID | None,
        map_type: FieldMapType,
        fields: list[FieldInput],
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> FieldMap:
        """Save fields using declarative approach - reconcile desired state with current."""
        field_map = await self.get_or_create_map(organization_id, map_type, direction)

        # Build lookup of existing fields by key
        fields_list: list[FieldMapField] = field_map.fields
        existing_by_key = {f.standard_field_key: f for f in fields_list}

        # Build set of incoming keys
        incoming_keys: set[str] = {f.standard_field_key for f in fields}

        # Process incoming fields
        for field_input in fields:
            existing_field = existing_by_key.get(field_input.standard_field_key)
            if existing_field:
                # Update existing field
                await self._update_field(existing_field, field_input)
            else:
                # Add new field (must be custom since defaults are auto-created)
                await self._add_custom_field(field_map.id, field_input, existing_by_key)

        # Delete fields not in incoming list (only custom fields)
        for key, existing_field in existing_by_key.items():
            if key not in incoming_keys:
                if existing_field.is_default:
                    raise CannotDeleteDefaultFieldError(
                        f"Cannot delete default field '{existing_field.standard_field_name}'"
                    )
                await self.repository.delete_field(existing_field.id)

        # Reload and return updated map
        updated_map = await self.repository.get_by_org_and_type(
            organization_id, map_type, direction
        )
        if not updated_map:
            raise RuntimeError("Field map not found after save")
        return updated_map

    async def _update_field(
        self,
        field: FieldMapField,
        field_input: FieldInput,
    ) -> None:
        """Update an existing field with input values."""
        # Validate: cannot edit standard_field_name or field_type for default fields
        if field.is_default:
            if field_input.standard_field_name is not None:
                raise CannotEditDefaultFieldError(
                    "Cannot edit standard_field_name of default field"
                )
            if field_input.field_type is not None:
                raise CannotEditDefaultFieldError(
                    "Cannot edit field_type of default field"
                )

        # Calculate linked based on organization_field_name
        will_be_linked = self._calculate_linked(field_input.organization_field_name)

        # Validate manufacturer/rep when linked
        new_manufacturer = (
            field_input.manufacturer
            if field_input.manufacturer is not None
            else field.manufacturer
        )
        new_rep = field_input.rep if field_input.rep is not None else field.rep

        if will_be_linked and (new_manufacturer is None or new_rep is None):
            raise LinkedFieldValidationError(
                "manufacturer and rep must be set when organization_field_name is provided"
            )

        # Apply updates
        field.organization_field_name = field_input.organization_field_name
        field.linked = will_be_linked

        if field_input.manufacturer is not None:
            field.manufacturer = field_input.manufacturer
        if field_input.rep is not None:
            field.rep = field_input.rep

        # For custom fields, allow updating name and type
        if not field.is_default:
            if field_input.standard_field_name is not None:
                field.standard_field_name = field_input.standard_field_name
            if field_input.field_type is not None:
                field.field_type = field_input.field_type.value

        await self.repository.update_field(field)

    async def _add_custom_field(
        self,
        field_map_id: uuid.UUID,
        field_input: FieldInput,
        existing_by_key: dict[str, FieldMapField],
    ) -> None:
        """Add a new custom field."""
        # Custom fields require these attributes
        if not field_input.standard_field_name:
            raise ValueError("standard_field_name is required for custom fields")
        if not field_input.field_type:
            raise ValueError("field_type is required for custom fields")
        if not field_input.category:
            raise ValueError("category is required for custom fields")

        # Generate unique key if needed
        existing_keys = set(existing_by_key.keys())
        key = generate_unique_field_key(field_input.standard_field_name, existing_keys)

        # Validate linked fields
        will_be_linked = self._calculate_linked(field_input.organization_field_name)
        if will_be_linked and (
            field_input.manufacturer is None or field_input.rep is None
        ):
            raise LinkedFieldValidationError(
                "manufacturer and rep must be set when organization_field_name is provided"
            )

        field = FieldMapField(
            field_map_id=field_map_id,
            standard_field_key=key,
            category=field_input.category.value,
            standard_field_name=field_input.standard_field_name,
            status=(field_input.status or FieldStatus.OPTIONAL).value,
            field_type=field_input.field_type.value,
            organization_field_name=field_input.organization_field_name,
            manufacturer=field_input.manufacturer,
            rep=field_input.rep,
            linked=will_be_linked,
            is_default=False,
        )
        await self.repository.add_field(field)

    @staticmethod
    def _create_default_fields(field_map_id: uuid.UUID) -> list[FieldMapField]:
        fields: list[FieldMapField] = []
        for config in DEFAULT_FIELDS:
            field = FieldMapField(
                field_map_id=field_map_id,
                standard_field_key=config.key,
                category=config.category.value,
                standard_field_name=config.standard_field_name,
                status=config.status.value,
                field_type=config.field_type.value,
                standard_field_name_description=config.description,
                preferred=config.preferred,
                is_default=True,
                display_order=config.order,
            )
            fields.append(field)
        return fields

    @staticmethod
    def _calculate_linked(organization_field_name: str | None) -> bool:
        return organization_field_name is not None and organization_field_name != ""

    @staticmethod
    def is_default_field_key(key: str) -> bool:
        return key in DEFAULT_FIELD_KEYS

    @staticmethod
    def get_default_config(key: str):
        return get_default_field_by_key(key)
