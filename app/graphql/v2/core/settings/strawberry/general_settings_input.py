from uuid import UUID

import strawberry
from commons.db.v6.core.settings.general_setting import GeneralSetting
from commons.db.v6.core.settings.setting_key import SettingKey as CommonsSettingKey

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.settings.strawberry.setting_key import SettingKey


@strawberry.input
class GeneralSettingsInput(BaseInputGQL[GeneralSetting]):
    key: SettingKey
    value: strawberry.scalars.JSON
    user_id: UUID | None = None

    def to_orm_model(self) -> GeneralSetting:
        return GeneralSetting(
            key=CommonsSettingKey[self.key.name],
            value=self.value,
            user_id=self.user_id,
        )
