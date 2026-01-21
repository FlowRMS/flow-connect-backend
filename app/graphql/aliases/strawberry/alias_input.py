from uuid import UUID

import strawberry
from commons.db.v6.core.aliases.alias_entity_type import AliasEntityType
from commons.db.v6.core.aliases.alias_model import Alias
from commons.db.v6.core.aliases.alias_sub_type import AliasSubType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class AliasInput(BaseInputGQL[Alias]):
    entity_id: UUID
    entity_type: AliasEntityType
    alias: str
    sub_type: AliasSubType | None = strawberry.UNSET

    def to_orm_model(self) -> Alias:
        return Alias(
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            sub_type=self.optional_field(self.sub_type),
            alias=self.alias,
        )
