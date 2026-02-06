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
class OrganizationPreferenceMutations:
    @strawberry.mutation()
    @inject
    async def update_organization_preference(
        self,
        application: Application,
        key: str,
        service: Injected[OrganizationPreferenceService],
        value: str | None = None,
    ) -> OrganizationPreferenceResponse:
        pref = await service.set_preference(
            application=application,
            key=key,
            value=value,
        )
        return OrganizationPreferenceResponse.from_model(pref)
