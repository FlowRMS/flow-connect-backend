from typing import Any
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.core.settings.general_setting import GeneralSetting
from commons.db.v6.core.settings.setting_key import SettingKey

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.settings.repositories.general_settings_repository import (
    GeneralSettingsRepository,
)


class GeneralSettingsService:
    def __init__(
        self,
        repository: GeneralSettingsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, setting_id: UUID) -> GeneralSetting:
        return await self.repository.get_by_id(setting_id)

    async def get_by_key(
        self,
        key: SettingKey,
        user_id: UUID | None = None,
    ) -> GeneralSetting:
        setting = await self.repository.get_by_key(key, user_id)
        if not setting:
            scope = "user" if user_id else "tenant"
            raise NotFoundError(f"Setting {key.name} not found for {scope}")
        return setting

    async def get_by_key_optional(
        self,
        key: SettingKey,
        user_id: UUID | None = None,
    ) -> GeneralSetting | None:
        return await self.repository.get_by_key(key, user_id)

    async def get_current_user_setting(self, key: SettingKey) -> GeneralSetting | None:
        return await self.repository.get_by_key(key, self.auth_info.flow_user_id)

    async def get_tenant_wide(self, key: SettingKey) -> GeneralSetting | None:
        return await self.repository.get_tenant_wide(key)

    async def list_by_user(self, user_id: UUID) -> list[GeneralSetting]:
        return await self.repository.list_by_user(user_id)

    async def list_current_user_settings(self) -> list[GeneralSetting]:
        return await self.repository.list_by_user(self.auth_info.flow_user_id)

    async def list_tenant_wide(self) -> list[GeneralSetting]:
        return await self.repository.list_tenant_wide()

    async def create(
        self,
        key: SettingKey,
        value: dict[str, Any],
        user_id: UUID | None = None,
    ) -> GeneralSetting:
        setting = GeneralSetting(key=key, value=value, user_id=user_id)
        return await self.repository.create(setting)

    async def create_for_current_user(
        self,
        key: SettingKey,
        value: dict[str, Any],
    ) -> GeneralSetting:
        return await self.create(key, value, self.auth_info.flow_user_id)

    async def create_tenant_wide(
        self,
        key: SettingKey,
        value: dict[str, Any],
    ) -> GeneralSetting:
        return await self.create(key, value, None)

    async def update(self, id: UUID, value: dict[str, Any]) -> GeneralSetting:
        setting = await self.repository.get_by_id(id)
        setting.value = value
        return await self.repository.update(setting)

    async def delete(
        self,
        key: SettingKey,
        user_id: UUID | None = None,
    ) -> bool:
        return await self.repository.delete_by_key(key, user_id)

    async def delete_for_current_user(self, key: SettingKey) -> bool:
        return await self.repository.delete_by_key(key, self.auth_info.flow_user_id)

    async def delete_tenant_wide(self, key: SettingKey) -> bool:
        return await self.repository.delete_by_key(key, None)
