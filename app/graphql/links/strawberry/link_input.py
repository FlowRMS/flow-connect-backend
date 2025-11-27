"""GraphQL input types for LinkRelation."""

from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


@strawberry.input
class LinkRelationInput(BaseInputGQL[LinkRelation]):
    """GraphQL input type for creating link relations."""

    source_entity_type: EntityType
    source_entity_id: UUID
    target_entity_type: EntityType
    target_entity_id: UUID

    def to_orm_model(self) -> LinkRelation:
        """Convert input to ORM model."""
        return LinkRelation(
            source_entity_type=self.source_entity_type,
            source_entity_id=self.source_entity_id,
            target_entity_type=self.target_entity_type,
            target_entity_id=self.target_entity_id,
        )


@strawberry.input
class DeleteLinkByEntitiesInput:
    """GraphQL input type for deleting a link by entity IDs."""

    source_entity_type: EntityType
    source_entity_id: UUID
    target_entity_type: EntityType
    target_entity_id: UUID
