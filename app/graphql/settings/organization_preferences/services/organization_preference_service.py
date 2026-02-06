import uuid
from collections import defaultdict
from enum import StrEnum

from commons.auth import AuthInfo

# Import registration to trigger preference config registration
import app.graphql.pos.preferences.registration  # noqa: F401
from app.graphql.connections.repositories.user_org_repository import UserOrgRepository
from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.exceptions import (
    InvalidApplicationError,
    InvalidPreferenceValueError,
)
from app.graphql.settings.organization_preferences.models.organization_preference import (
    OrganizationPreference,
)
from app.graphql.settings.organization_preferences.models.registry import (
    preference_registry,
)
from app.graphql.settings.organization_preferences.repositories.organization_preference_repository import (
    OrganizationPreferenceRepository,
)


class OrganizationPreferenceService:
    def __init__(
        self,
        repository: OrganizationPreferenceRepository,
        user_org_repository: UserOrgRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.user_org_repository = user_org_repository
        self.auth_info = auth_info

    async def _get_organization_id(self) -> uuid.UUID:
        if self.auth_info.auth_provider_id is None:
            raise InvalidApplicationError("User not authenticated")
        return await self.user_org_repository.get_user_org_id(
            self.auth_info.auth_provider_id
        )

    @staticmethod
    def _validate_application(application: Application | str) -> str:
        if isinstance(application, Application):
            return application.value
        if application not in [a.value for a in Application]:
            raise InvalidApplicationError(f"Invalid application: {application}")
        return application

    @staticmethod
    def _get_key_value(key: StrEnum | str) -> str:
        return key.value if isinstance(key, StrEnum) else key

    @staticmethod
    def _validate_preference_value(
        application: Application,
        key: StrEnum | str,
        value: str | None,
    ) -> None:
        if value is None:
            return
        key_str = OrganizationPreferenceService._get_key_value(key)
        allowed_values = preference_registry.get_allowed_values(
            application.value,
            key_str,
        )
        if allowed_values is not None and value not in allowed_values:
            raise InvalidPreferenceValueError(
                f"Invalid value '{value}' for {key_str}. "
                f"Must be one of: {allowed_values}"
            )

    async def get_preference(
        self,
        application: Application,
        key: StrEnum | str,
    ) -> str | None:
        organization_id = await self._get_organization_id()
        key_str = self._get_key_value(key)
        pref = await self.repository.get_by_org_application_key(
            organization_id=organization_id,
            application=application.value,
            key=key_str,
        )
        return pref.preference_value if pref else None

    async def get_preferences_by_application(
        self,
        application: Application,
    ) -> list[OrganizationPreference]:
        organization_id = await self._get_organization_id()
        return await self.repository.get_by_org_and_application(
            organization_id=organization_id,
            application=application.value,
        )

    async def get_all_preferences(self) -> dict[str, list[OrganizationPreference]]:
        organization_id = await self._get_organization_id()
        prefs = await self.repository.get_all_by_org(organization_id)
        result: dict[str, list[OrganizationPreference]] = defaultdict(list)
        for pref in prefs:
            result[pref.application].append(pref)
        return dict(result)

    async def set_preference(
        self,
        application: Application | str,
        key: StrEnum | str,
        value: str | None,
    ) -> OrganizationPreference:
        application_str = self._validate_application(application)
        application_enum = Application(application_str)
        self._validate_preference_value(application_enum, key, value)
        key_str = self._get_key_value(key)
        organization_id = await self._get_organization_id()

        return await self.repository.upsert(
            organization_id=organization_id,
            application=application_str,
            key=key_str,
            value=value,
        )
