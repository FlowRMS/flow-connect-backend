import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.services.organization_preference_service import (
    OrganizationPreferenceService,
)
from app.graphql.settings.organization_preferences.strawberry.organization_preference_types import (
    OrganizationPreferenceResponse,
)


@strawberry.type
class OrganizationPreferenceQueries:
    @strawberry.field()
    @inject
    async def organization_preference(
        self,
        application: Application,
        key: str,
        service: Injected[OrganizationPreferenceService],
    ) -> OrganizationPreferenceResponse | None:
        value = await service.get_preference(application, key)
        if value is None:
            return None
        return OrganizationPreferenceResponse(
            application=application,
            key=key,
            value=value,
        )

    @strawberry.field()
    @inject
    async def organization_preferences_by_application(
        self,
        application: Application,
        service: Injected[OrganizationPreferenceService],
    ) -> list[OrganizationPreferenceResponse]:
        prefs = await service.get_preferences_by_application(application)
        return [OrganizationPreferenceResponse.from_model(p) for p in prefs]

    @strawberry.field()
    @inject
    async def organization_preferences(
        self,
        service: Injected[OrganizationPreferenceService],
    ) -> list[OrganizationPreferenceResponse]:
        prefs_by_app = await service.get_all_preferences()
        result: list[OrganizationPreferenceResponse] = []
        for prefs in prefs_by_app.values():
            result.extend(OrganizationPreferenceResponse.from_model(p) for p in prefs)
        return result
