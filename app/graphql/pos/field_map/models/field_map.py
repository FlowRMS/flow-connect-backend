from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from commons.db.v6.user.user import HasCreatedBy, User
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldMapDirection,
    FieldMapType,
    FieldStatus,
    FieldType,
)


class FieldMap(PyConnectPosBaseModel, HasCreatedBy, HasCreatedAt, kw_only=True):
    __tablename__ = "field_maps"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "map_type",
            "direction",
            name="uq_field_maps_org_type_direction",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    map_type: Mapped[str] = mapped_column(String(10), nullable=False)
    direction: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=FieldMapDirection.SEND,
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        default=None,
    )

    fields: Mapped[list[FieldMapField]] = relationship(
        "FieldMapField",
        back_populates="field_map",
        cascade="all, delete-orphan",
        init=False,
    )
    created_by: Mapped[User] = relationship(init=False)

    @property
    def map_type_enum(self) -> FieldMapType:
        return FieldMapType(self.map_type)

    @property
    def direction_enum(self) -> FieldMapDirection:
        return FieldMapDirection(self.direction)


class FieldMapField(PyConnectPosBaseModel, kw_only=True):
    __tablename__ = "field_map_fields"
    __table_args__ = (
        UniqueConstraint(
            "field_map_id",
            "standard_field_key",
            name="uq_field_map_fields_map_key",
        ),
        {"schema": "connect_pos", "extend_existing": True},
    )

    # Required fields (no defaults) - must come first
    field_map_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("connect_pos.field_maps.id", ondelete="CASCADE"),
        nullable=False,
    )
    standard_field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    standard_field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Optional fields (with defaults) - must come after required fields
    standard_field_name_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    organization_field_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default=None,
    )
    manufacturer: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
    )
    rep: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
    )
    linked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    preferred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    field_map: Mapped[FieldMap] = relationship(
        "FieldMap",
        back_populates="fields",
        init=False,
    )

    @property
    def category_enum(self) -> FieldCategory:
        return FieldCategory(self.category)

    @property
    def status_enum(self) -> FieldStatus:
        return FieldStatus(self.status)

    @property
    def field_type_enum(self) -> FieldType:
        return FieldType(self.field_type)
