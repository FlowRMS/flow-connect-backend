"""Landing page response type for Notes entity."""

from typing import Any, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageInterfaceBase
from app.graphql.common.linked_entity import LinkedEntity


@strawberry.type(name="NoteLandingPage")
class NoteLandingPageResponse(LandingPageInterfaceBase):
    """Landing page response for notes with key fields for list views."""

    title: str
    content: str
    tags: list[str] | None
    mentions: list[UUID] | None
    linked_entities: list[LinkedEntity]

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        """Create an instance from a SQLAlchemy Row result."""
        data = cls.unpack_row(row)
        linked_entities_data = data.pop("linked_entities", [])
        data["linked_entities"] = [
            LinkedEntity(
                id=UUID(item["id"]),
                title=item["title"],
                entity_type=EntityType(item["entity_type"]),
            )
            for item in linked_entities_data
        ]
        return cls(**data)
