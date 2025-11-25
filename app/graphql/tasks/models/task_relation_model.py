from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel, HasPrimaryKey
from app.graphql.tasks.models.related_entity_type import RelatedEntityType


class TaskRelation(BaseModel, HasPrimaryKey, kw_only=True):
    """Task relation entity representing relationships between tasks and other entities."""

    __tablename__ = "task_relations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id"],
            ["crm.tasks.id"],
            name="fk_task_relations_task_id",
        ),
        Index(
            "ix_crm_task_relations_task_id_related_type_related_id",
            "task_id",
            "related_type",
            "related_id",
        ),
        {"schema": "crm"},
    )

    # Required fields
    task_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    related_type: Mapped[RelatedEntityType] = mapped_column(
        IntEnum(RelatedEntityType), nullable=False
    )
    related_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
