from typing import Any
from uuid import UUID

from commons.db.v6.core.settings.general_setting import GeneralSetting
from commons.db.v6.core.settings.setting_key import SettingKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class GeneralSettingsRepository(BaseRepository[GeneralSetting]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            GeneralSetting,
        )

    async def get_by_key(
        self,
        key: SettingKey,
        user_id: UUID | None = None,
    ) -> GeneralSetting | None:
        stmt = select(GeneralSetting).where(
            GeneralSetting.key == key,
            GeneralSetting.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_key_for_user(
        self,
        key: SettingKey,
        user_id: UUID,
    ) -> GeneralSetting | None:
        return await self.get_by_key(key, user_id)

    async def get_tenant_wide(self, key: SettingKey) -> GeneralSetting | None:
        return await self.get_by_key(key, None)

    async def list_by_user(self, user_id: UUID) -> list[GeneralSetting]:
        stmt = select(GeneralSetting).where(GeneralSetting.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_tenant_wide(self) -> list[GeneralSetting]:
        stmt = select(GeneralSetting).where(GeneralSetting.user_id.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        key: SettingKey,
        value: dict[str, Any],
        user_id: UUID | None = None,
    ) -> GeneralSetting:
        existing = await self.get_by_key(key, user_id)
        if existing:
            existing.value = value
            await self.session.flush()
            return existing

        setting = GeneralSetting(key=key, value=value, user_id=user_id)
        return await self.create(setting)

    async def delete_by_key(
        self,
        key: SettingKey,
        user_id: UUID | None = None,
    ) -> bool:
        existing = await self.get_by_key(key, user_id)
        if not existing:
            return False
        await self.session.delete(existing)
        await self.session.flush()
        return True
