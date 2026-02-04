from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.settings.general_setting import GeneralSetting

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.settings.strawberry.setting_key import SettingKey


@strawberry.type
class GeneralSettingsResponse(DTOMixin[GeneralSetting]):
    _instance: strawberry.Private[GeneralSetting]
    id: UUID
    key: SettingKey
    value: strawberry.scalars.JSON
    user_id: UUID | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: GeneralSetting) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            key=SettingKey[model.key.name],
            value=model.value,
            user_id=model.user_id,
            created_at=model.created_at,
        )
