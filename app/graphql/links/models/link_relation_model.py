"""LinkRelation ORM model."""

from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.links.models.entity_type import EntityType


class LinkRelation(BaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Link relation entity representing bidirectional relationships between any two entities."""

    __tablename__ = "link_relations"
    __table_args__ = (
        Index(
            "ix_crm_link_relations_source_type_source_id",
            "source_entity_type",
            "source_entity_id",
        ),
        Index(
            "ix_crm_link_relations_target_type_target_id",
            "target_entity_type",
            "target_entity_id",
        ),
        Index(
            "ix_crm_link_relations_source_target",
            "source_entity_type",
            "source_entity_id",
            "target_entity_type",
            "target_entity_id",
        ),
        {"schema": "crm"},
    )

    # Source entity
    source_entity_type: Mapped[EntityType] = mapped_column(
        IntEnum(EntityType), nullable=False
    )
    source_entity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )

    # Target entity
    target_entity_type: Mapped[EntityType] = mapped_column(
        IntEnum(EntityType), nullable=False
    )
    target_entity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
