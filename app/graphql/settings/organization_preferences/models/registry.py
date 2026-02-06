from app.graphql.settings.organization_preferences.models.types import (
    PreferenceKeyConfig,
)


class PreferenceConfigRegistry:
    def __init__(self) -> None:
        self._configs: dict[str, dict[str, PreferenceKeyConfig]] = {}

    def register(
        self,
        application: str,
        config: dict[str, PreferenceKeyConfig],
    ) -> None:
        self._configs[application] = config

    def get_config(
        self,
        application: str,
    ) -> dict[str, PreferenceKeyConfig] | None:
        return self._configs.get(application)

    def get_allowed_values(
        self,
        application: str,
        key: str,
    ) -> list[str] | None:
        app_config = self._configs.get(application)
        if not app_config:
            return None
        key_config = app_config.get(key)
        if not key_config:
            return None
        return key_config.allowed_values


preference_registry = PreferenceConfigRegistry()
