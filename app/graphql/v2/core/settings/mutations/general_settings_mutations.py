from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.settings.setting_key import SettingKey as CommonsSettingKey

from app.graphql.inject import inject
from app.graphql.v2.core.settings.services.general_settings_service import (
    GeneralSettingsService,
)
from app.graphql.v2.core.settings.strawberry.general_settings_input import (
    GeneralSettingsInput,
)
from app.graphql.v2.core.settings.strawberry.general_settings_response import (
    GeneralSettingsResponse,
)
from app.graphql.v2.core.settings.strawberry.setting_key import SettingKey


@strawberry.type
class GeneralSettingsMutations:
    @strawberry.mutation
    @inject
    async def create_general_setting(
        self,
        input: GeneralSettingsInput,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse:
        setting = await service.create(
            key=CommonsSettingKey[input.key.name],
            value=input.value,
            user_id=input.user_id,
        )
        return GeneralSettingsResponse.from_orm_model(setting)

    @strawberry.mutation
    @inject
    async def update_general_setting(
        self,
        id: UUID,
        value: strawberry.scalars.JSON,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse:
        setting = await service.update(id=id, value=value)
        return GeneralSettingsResponse.from_orm_model(setting)

    @strawberry.mutation
    @inject
    async def create_my_setting(
        self,
        key: SettingKey,
        value: strawberry.scalars.JSON,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse:
        setting = await service.create_for_current_user(
            key=CommonsSettingKey[key.name],
            value=value,
        )
        return GeneralSettingsResponse.from_orm_model(setting)

    @strawberry.mutation
    @inject
    async def create_tenant_setting(
        self,
        key: SettingKey,
        value: strawberry.scalars.JSON,
        service: Injected[GeneralSettingsService],
    ) -> GeneralSettingsResponse:
        setting = await service.create_tenant_wide(
            key=CommonsSettingKey[key.name],
            value=value,
        )
        return GeneralSettingsResponse.from_orm_model(setting)

    @strawberry.mutation
    @inject
    async def delete_general_setting(
        self,
        key: SettingKey,
        user_id: UUID | None,
        service: Injected[GeneralSettingsService],
    ) -> bool:
        return await service.delete(CommonsSettingKey[key.name], user_id)

    @strawberry.mutation
    @inject
    async def delete_my_setting(
        self,
        key: SettingKey,
        service: Injected[GeneralSettingsService],
    ) -> bool:
        return await service.delete_for_current_user(CommonsSettingKey[key.name])

    @strawberry.mutation
    @inject
    async def delete_tenant_setting(
        self,
        key: SettingKey,
        service: Injected[GeneralSettingsService],
    ) -> bool:
        return await service.delete_tenant_wide(CommonsSettingKey[key.name])
