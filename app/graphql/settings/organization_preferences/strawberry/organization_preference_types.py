import strawberry

from app.graphql.pos.preferences.enums import RoutingMethod, TransferMethod
from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.models.organization_preference import (
    OrganizationPreference,
)

# Register enums with Strawberry
strawberry.enum(Application)
strawberry.enum(TransferMethod)
strawberry.enum(RoutingMethod)


@strawberry.type
class OrganizationPreferenceResponse:
    application: Application
    key: str
    value: str | None

    @staticmethod
    def from_model(pref: OrganizationPreference) -> "OrganizationPreferenceResponse":
        return OrganizationPreferenceResponse(
            application=Application(pref.application),
            key=pref.preference_key,
            value=pref.preference_value,
        )
