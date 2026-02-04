from decimal import Decimal

import strawberry

from app.graphql.common.strawberry.overage_record import OverageTypeEnum


@strawberry.input
class FactoryOverageSettingsInput:
    overage_allowed: bool = False
    overage_type: OverageTypeEnum = OverageTypeEnum.BY_LINE
    rep_overage_share: Decimal = Decimal("100.00")
