from enum import Enum

import strawberry
from commons.db.v6 import AutoNumberEntityType


@strawberry.enum
class AutoNumberEntityTypeEnum(Enum):
    PRE_OPPORTUNITIES = "pre_opportunities"
    JOBS = "jobs"
    QUOTES = "quotes"
    ORDERS = "orders"
    ORDER_ACKNOWLEDGEMENTS = "order_acknowledgements"
    INVOICES = "invoices"
    CHECKS = "checks"

    def to_entity_type(self) -> AutoNumberEntityType:
        mapping = {
            AutoNumberEntityTypeEnum.PRE_OPPORTUNITIES: (
                AutoNumberEntityType.PRE_OPPORTUNITY
            ),
            AutoNumberEntityTypeEnum.JOBS: AutoNumberEntityType.JOB,
            AutoNumberEntityTypeEnum.QUOTES: AutoNumberEntityType.QUOTE,
            AutoNumberEntityTypeEnum.ORDERS: AutoNumberEntityType.ORDER,
            AutoNumberEntityTypeEnum.ORDER_ACKNOWLEDGEMENTS: (
                AutoNumberEntityType.ORDER_ACKNOWLEDGEMENT
            ),
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
            AutoNumberEntityType.PRE_OPPORTUNITY: cls.PRE_OPPORTUNITIES,
            AutoNumberEntityType.JOB: cls.JOBS,
            AutoNumberEntityType.QUOTE: cls.QUOTES,
            AutoNumberEntityType.ORDER: cls.ORDERS,
            AutoNumberEntityType.ORDER_ACKNOWLEDGEMENT: cls.ORDER_ACKNOWLEDGEMENTS,
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
