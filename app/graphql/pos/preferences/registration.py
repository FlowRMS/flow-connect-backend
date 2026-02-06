from app.graphql.pos.preferences.config import POS_PREFERENCE_CONFIG
from app.graphql.settings.applications.models.enums import Application
from app.graphql.settings.organization_preferences.models.registry import (
    preference_registry,
)

preference_registry.register(Application.POS.value, POS_PREFERENCE_CONFIG)
