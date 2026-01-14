from collections.abc import Iterable, Sequence

from commons.db.v6 import AutoNumberEntityType, AutoNumberSetting
from sqlalchemy.exc import IntegrityError

from app.graphql.auto_numbers.repositories.auto_number_settings_repository import (
    AutoNumberSettingsRepository,
)
from app.graphql.auto_numbers.strawberry.auto_number_settings_input import (
    AutoNumberSettingsInput,
)


class AutoNumberSettingsService:
    def __init__(
        self,
        repository: AutoNumberSettingsRepository,
    ) -> None:
        super().__init__()
        self.repository = repository

    async def get_settings(self) -> list[AutoNumberSetting]:
        settings = await self.repository.list_all()
        settings_by_type = {setting.entity_type: setting for setting in settings}
        missing_types = [
            entity_type
            for entity_type in AutoNumberEntityType
            if entity_type not in settings_by_type
        ]
        if not missing_types:
            return settings

        created_settings = await self._create_defaults(missing_types)
        return settings + created_settings

    async def update_settings(
        self,
        inputs: Sequence[AutoNumberSettingsInput],
    ) -> list[AutoNumberSetting]:
        if not inputs:
            return []

        entity_types = [inp.entity_type.to_entity_type() for inp in inputs]
        existing = await self.repository.list_by_entity_types(entity_types)
        existing_by_type = {setting.entity_type: setting for setting in existing}

        updated: list[AutoNumberSetting] = []
        for input_data in inputs:
            entity_type = input_data.entity_type.to_entity_type()
            setting = existing_by_type.get(entity_type)
            if not setting:
                setting = AutoNumberSetting(
                    entity_type=entity_type,
                    prefix=input_data.prefix,
                    starts_at=input_data.starts_at,
                    increment_by=input_data.increment_by,
                    counter=input_data.starts_at,
                    allow_auto_generation=input_data.allow_auto_generation,
                )
                updated.append(await self.repository.create(setting))
                continue

            if input_data.starts_at != setting.starts_at:
                setting.starts_at = input_data.starts_at
                setting.counter = input_data.starts_at
            setting.prefix = input_data.prefix
            setting.increment_by = input_data.increment_by
            setting.allow_auto_generation = input_data.allow_auto_generation

            updated.append(await self.repository.save(setting))

        return updated

    async def generate_number(self, entity_type: AutoNumberEntityType) -> str:
        setting = await self._get_or_create_for_update(entity_type)

        if not setting.allow_auto_generation:
            setting.allow_auto_generation = True

        if setting.counter < setting.starts_at:
            setting.counter = setting.starts_at

        next_value = setting.counter
        increment = setting.increment_by if setting.increment_by > 0 else 1
        setting.counter = next_value + increment

        _ = await self.repository.save(setting)
        return f"{setting.prefix}{next_value}"

    @staticmethod
    def needs_generation(value: str | None) -> bool:
        return value is None or not value.strip()

    async def _get_or_create_for_update(
        self,
        entity_type: AutoNumberEntityType,
    ) -> AutoNumberSetting:
        setting = await self.repository.get_by_entity_type_for_update(entity_type)
        if setting:
            return setting

        default_setting = AutoNumberSetting(
            entity_type=entity_type,
            prefix="Flow-",
            starts_at=1,
            increment_by=1,
            counter=1,
            allow_auto_generation=True,
        )
        try:
            return await self.repository.create(default_setting)
        except IntegrityError:
            setting = await self.repository.get_by_entity_type_for_update(entity_type)
            if setting is None:
                raise ValueError(
                    f"Auto number settings missing for entity type {entity_type}"
                )
            return setting

    async def _create_defaults(
        self,
        entity_types: Iterable[AutoNumberEntityType],
    ) -> list[AutoNumberSetting]:
        created: list[AutoNumberSetting] = []
        for entity_type in entity_types:
            setting = AutoNumberSetting(
                entity_type=entity_type,
                prefix="Flow-",
                starts_at=1,
                increment_by=1,
                counter=1,
                allow_auto_generation=True,
            )
            try:
                created.append(await self.repository.create(setting))
            except IntegrityError:
                existing = await self.repository.get_by_entity_type(entity_type)
                if existing is not None:
                    created.append(existing)
        return created
