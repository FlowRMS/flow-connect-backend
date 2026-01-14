from enum import Enum

import strawberry
from commons.db.v6 import AutoNumberEntityType


@strawberry.enum
class AutoNumberEntityTypeEnum(Enum):
    QUOTES = "quotes"
    ORDERS = "orders"
    INVOICES = "invoices"
    CHECKS = "checks"

    def to_entity_type(self) -> AutoNumberEntityType:
        mapping = {
            AutoNumberEntityTypeEnum.QUOTES: AutoNumberEntityType.QUOTE,
            AutoNumberEntityTypeEnum.ORDERS: AutoNumberEntityType.ORDER,
            AutoNumberEntityTypeEnum.INVOICES: AutoNumberEntityType.INVOICE,
            AutoNumberEntityTypeEnum.CHECKS: AutoNumberEntityType.CHECK,
        }
        return mapping[self]

    @classmethod
    def from_entity_type(
        cls,
        entity_type: AutoNumberEntityType,
    ) -> "AutoNumberEntityTypeEnum":
        mapping = {
            AutoNumberEntityType.QUOTE: cls.QUOTES,
            AutoNumberEntityType.ORDER: cls.ORDERS,
            AutoNumberEntityType.INVOICE: cls.INVOICES,
            AutoNumberEntityType.CHECK: cls.CHECKS,
        }
        return mapping[entity_type]


@strawberry.input
class AutoNumberSettingsInput:
    entity_type: AutoNumberEntityTypeEnum
    prefix: str
    starts_at: int
    increment_by: int
    allow_auto_generation: bool = True
