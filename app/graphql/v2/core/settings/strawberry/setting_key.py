from enum import Enum

import strawberry


@strawberry.enum
class SettingKey(Enum):
    """GraphQL enum for setting keys.

    This mirrors the values from commons.db.v6.core.settings.setting_key.SettingKey
    but is decorated with @strawberry.enum for proper GraphQL Federation support.
    """

    QUOTE_SETTINGS = "QUOTE_SETTINGS"
    ORDER_SETTINGS = "ORDER_SETTINGS"
    INVOICE_SETTINGS = "INVOICE_SETTINGS"
    CHECKS_SETTINGS = "CHECKS_SETTINGS"
    CHAT_SETTINGS = "CHAT_SETTINGS"
    SIDEBAR_SETTINGS = "SIDEBAR_SETTINGS"
    PICKLIST_SETTINGS = "PICKLIST_SETTINGS"
    NOTIFICATION_SETTINGS = "NOTIFICATION_SETTINGS"
