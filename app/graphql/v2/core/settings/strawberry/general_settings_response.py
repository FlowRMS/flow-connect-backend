from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.settings.general_setting import GeneralSetting
from commons.db.v6.core.settings.setting_key import SettingKey

from app.core.db.adapters.dto import DTOMixin


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
            key=SettingKey(model.key.value),
            value=model.value,
            user_id=model.user_id,
            created_at=model.created_at,
        )
