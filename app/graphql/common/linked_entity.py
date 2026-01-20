"""Common type for linked entities."""

from uuid import UUID

import strawberry
from commons.db.v6.crm.links.entity_type import EntityType


@strawberry.type(name="LinkedEntity")
class LinkedEntity:
    """Represents a linked entity with its id, title, and type."""

    id: UUID | None
    title: str | None
    entity_type: EntityType | None
