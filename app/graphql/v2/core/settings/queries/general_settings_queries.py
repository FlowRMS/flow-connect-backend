from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.settings.setting_key import SettingKey as CommonsSettingKey

from app.graphql.inject import inject
from app.graphql.v2.core.settings.services.general_settings_service import (
    GeneralSettingsService,
)
from app.graphql.v2.core.settings.strawberry.general_settings_response import (
    GeneralSettingsResponse,
)
from app.graphql.v2.core.settings.strawberry.setting_key import SettingKey


@strawberry.type
class GeneralSettingsQueries:
    @strawberry.field
    @inject
    async def general_setting(
        self,
        key: SettingKey,
        user_id: UUID | None,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse | None:
        setting = await service.get_by_key_optional(
            CommonsSettingKey[key.name], user_id
        )
        return GeneralSettingsResponse.from_orm_model_optional(setting)

    @strawberry.field
    @inject
    async def my_setting(
        self,
        key: SettingKey,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse | None:
        setting = await service.get_current_user_setting(CommonsSettingKey[key.name])
        return GeneralSettingsResponse.from_orm_model_optional(setting)

    @strawberry.field
    @inject
    async def tenant_setting(
        self,
        key: SettingKey,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse | None:
        setting = await service.get_tenant_wide(CommonsSettingKey[key.name])
        return GeneralSettingsResponse.from_orm_model_optional(setting)

    @strawberry.field
    @inject
    async def my_settings(
        self,
        service: Injected[GeneralSettingsService],
    ) -> list[GeneralSettingsResponse]:
        settings = await service.list_current_user_settings()
        return GeneralSettingsResponse.from_orm_model_list(settings)

    @strawberry.field
    @inject
    async def tenant_settings(
        self,
        service: Injected[GeneralSettingsService],
    ) -> list[GeneralSettingsResponse]:
        settings = await service.list_tenant_wide()
        return GeneralSettingsResponse.from_orm_model_list(settings)

    @strawberry.field
    @inject
    async def user_settings(
        self,
        user_id: UUID,
        service: Injected[GeneralSettingsService],
    ) -> list[GeneralSettingsResponse]:
        settings = await service.list_by_user(user_id)
        return GeneralSettingsResponse.from_orm_model_list(settings)
