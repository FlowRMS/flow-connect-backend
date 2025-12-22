"""GraphQL response types for LinkRelation."""

from datetime import datetime
from uuid import UUID

import strawberry
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class LinkRelationType(DTOMixin[LinkRelation]):
    """GraphQL type for LinkRelation entity (output/query results)."""

    id: UUID
    source_entity_type: EntityType
    source_entity_id: UUID
    target_entity_type: EntityType
    target_entity_id: UUID
    created_at: datetime
    # created_by: UUID

    @classmethod
    def from_orm_model(cls, model: LinkRelation) -> "LinkRelationType":
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            source_entity_type=model.source_entity_type,
            source_entity_id=model.source_entity_id,
            target_entity_type=model.target_entity_type,
            target_entity_id=model.target_entity_id,
            created_at=model.created_at,
            # created_by=model.created_by,
        )
