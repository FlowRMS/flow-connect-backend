from uuid import UUID

import strawberry
from commons.db.v6.core.settings.general_setting import GeneralSetting
from commons.db.v6.core.settings.setting_key import SettingKey

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class GeneralSettingsInput(BaseInputGQL[GeneralSetting]):
    key: SettingKey
    value: strawberry.scalars.JSON
    user_id: UUID | None = None

    def to_orm_model(self) -> GeneralSetting:
        return GeneralSetting(
            key=SettingKey(self.key.value),
            value=self.value,
            user_id=self.user_id,
        )
