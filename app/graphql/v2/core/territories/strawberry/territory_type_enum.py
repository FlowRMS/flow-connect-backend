from enum import Enum

import strawberry
from commons.db.v6.core.territories.territory_type_enum import (
    TerritoryTypeEnum as DBTerritoryTypeEnum,
)


@strawberry.enum
class TerritoryTypeEnum(Enum):
    REGION = DBTerritoryTypeEnum.REGION
    SUBREGION = DBTerritoryTypeEnum.SUBREGION
    TERRITORY = DBTerritoryTypeEnum.TERRITORY
