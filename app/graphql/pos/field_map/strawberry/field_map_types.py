import uuid

import strawberry

from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_config import (
    CATEGORY_CONFIG,
    DEFAULT_FIELDS,
    CategoryConfig,
    DefaultFieldConfig,
)
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldMapDirection,
    FieldMapType,
    FieldStatus,
    FieldType,
)

# Register enums with Strawberry
FieldMapTypeEnum = strawberry.enum(FieldMapType)
FieldMapDirectionEnum = strawberry.enum(FieldMapDirection)
FieldStatusEnum = strawberry.enum(FieldStatus)
FieldTypeEnum = strawberry.enum(FieldType)
FieldCategoryEnum = strawberry.enum(FieldCategory)


@strawberry.type
class CategoryConfigResponse:
    category: FieldCategory
    name: str
    description: str
    order: int
    visible: bool

    @staticmethod
    def from_config(
        category: FieldCategory, config: CategoryConfig
    ) -> "CategoryConfigResponse":
        return CategoryConfigResponse(
            category=category,
            name=config.name,
            description=config.description,
            order=config.order,
            visible=config.visible,
        )

    @staticmethod
    def get_all() -> list["CategoryConfigResponse"]:
        return [
            CategoryConfigResponse.from_config(cat, config)
            for cat, config in CATEGORY_CONFIG.items()
        ]


@strawberry.type
class FieldMapFieldResponse:
    id: strawberry.ID | None
    standard_field_key: str
    category: FieldCategory
    standard_field_name: str
    standard_field_name_description: str | None
    organization_field_name: str | None
    status: FieldStatus
    manufacturer: bool | None
    rep: bool | None
    linked: bool
    preferred: bool
    is_default: bool
    field_type: FieldType
    display_order: int

    @staticmethod
    def from_model(field: FieldMapField) -> "FieldMapFieldResponse":
        return FieldMapFieldResponse(
            id=strawberry.ID(str(field.id)),
            standard_field_key=field.standard_field_key,
            category=FieldCategory(field.category),
            standard_field_name=field.standard_field_name,
            standard_field_name_description=field.standard_field_name_description,
            organization_field_name=field.organization_field_name,
            status=FieldStatus(field.status),
            manufacturer=field.manufacturer,
            rep=field.rep,
            linked=field.linked,
            preferred=field.preferred,
            is_default=field.is_default,
            field_type=FieldType(field.field_type),
            display_order=field.display_order,
        )

    @staticmethod
    def from_default_config(config: DefaultFieldConfig) -> "FieldMapFieldResponse":
        return FieldMapFieldResponse(
            id=None,
            standard_field_key=config.key,
            category=config.category,
            standard_field_name=config.standard_field_name,
            standard_field_name_description=config.description,
            organization_field_name=None,
            status=config.status,
            manufacturer=None,
            rep=None,
            linked=False,
            preferred=config.preferred,
            is_default=True,
            field_type=config.field_type,
            display_order=config.order,
        )


@strawberry.type
class FieldMapResponse:
    id: strawberry.ID | None
    organization_id: strawberry.ID | None
    map_type: FieldMapType
    direction: FieldMapDirection
    fields: list[FieldMapFieldResponse]
    categories: list[CategoryConfigResponse]

    @staticmethod
    def from_model(field_map: FieldMap) -> "FieldMapResponse":
        return FieldMapResponse(
            id=strawberry.ID(str(field_map.id)),
            organization_id=(
                strawberry.ID(str(field_map.organization_id))
                if field_map.organization_id
                else None
            ),
            map_type=FieldMapType(field_map.map_type),
            direction=FieldMapDirection(field_map.direction),
            fields=[FieldMapFieldResponse.from_model(f) for f in field_map.fields],
            categories=CategoryConfigResponse.get_all(),
        )

    @staticmethod
    def from_defaults(
        organization_id: uuid.UUID | None,
        map_type: FieldMapType,
        direction: FieldMapDirection,
    ) -> "FieldMapResponse":
        return FieldMapResponse(
            id=None,
            organization_id=(
                strawberry.ID(str(organization_id)) if organization_id else None
            ),
            map_type=map_type,
            direction=direction,
            fields=[
                FieldMapFieldResponse.from_default_config(config)
                for config in DEFAULT_FIELDS
            ],
            categories=CategoryConfigResponse.get_all(),
        )


# noinspection DuplicatedCode
# Intentional code duplication - Service layer uses dataclass, GraphQL layer uses strawberry.input (separation of concerns)
@strawberry.input
class FieldInput:
    """Input for a field - used for both default and custom fields."""

    standard_field_key: str
    organization_field_name: str | None = None
    manufacturer: bool | None = None
    rep: bool | None = None
    # Only required for custom fields (non-default keys)
    standard_field_name: str | None = None
    field_type: FieldType | None = None
    category: FieldCategory | None = None
    status: FieldStatus | None = None


@strawberry.input
class SaveFieldMapInput:
    """Declarative input - send the desired state, backend reconciles."""

    map_type: FieldMapType
    fields: list[FieldInput]
    organization_id: strawberry.ID | None = None
    direction: FieldMapDirection = FieldMapDirection.SEND
