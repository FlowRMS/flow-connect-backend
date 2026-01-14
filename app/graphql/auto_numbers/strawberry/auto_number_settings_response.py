from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import AutoNumberSetting

from app.core.db.adapters.dto import DTOMixin
from app.graphql.auto_numbers.strawberry.auto_number_settings_input import (
    AutoNumberEntityTypeEnum,
)


@strawberry.type
class AutoNumberSettingsResponse(DTOMixin[AutoNumberSetting]):
    id: UUID
    entity_type: AutoNumberEntityTypeEnum
    prefix: str
    starts_at: int
    increment_by: int
    counter: int
    allow_auto_generation: bool

    @classmethod
    def from_orm_model(cls, model: AutoNumberSetting) -> Self:
        return cls(
            id=model.id,
            entity_type=AutoNumberEntityTypeEnum.from_entity_type(model.entity_type),
            prefix=model.prefix,
            starts_at=model.starts_at,
            increment_by=model.increment_by,
            counter=model.counter,
            allow_auto_generation=model.allow_auto_generation,
        )
