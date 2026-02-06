from app.graphql.pos.preferences.enums import (
    PosPreferenceKey,
    RoutingMethod,
    TransferMethod,
)
from app.graphql.settings.organization_preferences.models.types import (
    PreferenceKeyConfig,
)

POS_PREFERENCE_CONFIG: dict[str, PreferenceKeyConfig] = {
    PosPreferenceKey.SEND_METHOD.value: PreferenceKeyConfig(
        allowed_values=[m.value for m in TransferMethod],
    ),
    PosPreferenceKey.RECEIVING_METHOD.value: PreferenceKeyConfig(
        allowed_values=[m.value for m in TransferMethod],
    ),
    PosPreferenceKey.ROUTING_METHOD.value: PreferenceKeyConfig(
        allowed_values=[m.value for m in RoutingMethod],
    ),
    PosPreferenceKey.MANUFACTURER_PART_NUMBER_PREFIX_REMOVAL.value: PreferenceKeyConfig(
        allowed_values=["true", "false"],
    ),
    # MANUFACTURER_COLUMN has no validation - accepts any text
}
