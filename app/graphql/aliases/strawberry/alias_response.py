from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.aliases.alias_entity_type import AliasEntityType
from commons.db.v6.core.aliases.alias_model import Alias
from commons.db.v6.core.aliases.alias_sub_type import AliasSubType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class AliasType(DTOMixin[Alias]):
    id: UUID
    entity_id: UUID
    entity_type: AliasEntityType
    sub_type: AliasSubType | None
    alias: str
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: Alias) -> Self:
        return cls(
            id=model.id,
            entity_id=model.entity_id,
            entity_type=model.entity_type,
            sub_type=model.sub_type,
            alias=model.alias,
            created_at=model.created_at,
        )
