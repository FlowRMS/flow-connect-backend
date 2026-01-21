import strawberry
from commons.db.v6 import AutoNumberEntityType


@strawberry.input
class AutoNumberSettingsInput:
    entity_type: AutoNumberEntityType
    prefix: str
    starts_at: int
    increment_by: int
    allow_auto_generation: bool = True
