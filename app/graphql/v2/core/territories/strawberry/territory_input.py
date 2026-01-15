from uuid import UUID

import strawberry
from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_type_enum import (
    TerritoryTypeEnum as DBTerritoryTypeEnum,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.territories.strawberry.territory_split_rate_input import (
    TerritorySplitRateInput,
)
from app.graphql.v2.core.territories.strawberry.territory_type_enum import (
    TerritoryTypeEnum,
)


@strawberry.input
class TerritoryInput(BaseInputGQL[Territory]):
    name: str
    code: str
    territory_type: TerritoryTypeEnum
    parent_id: UUID | None = None
    zip_codes: list[str] = strawberry.field(default_factory=list)
    county_codes: list[str] = strawberry.field(default_factory=list)
    city_names: list[str] = strawberry.field(default_factory=list)
    state_codes: list[str] = strawberry.field(default_factory=list)
    active: bool = True
    split_rates: list[TerritorySplitRateInput] = strawberry.field(default_factory=list)

    def to_orm_model(self) -> Territory:
        territory = Territory(
            name=self.name,
            code=self.code,
            territory_type=DBTerritoryTypeEnum(self.territory_type.value),
            parent_id=self.parent_id,
            zip_codes=self.zip_codes,
            county_codes=self.county_codes,
            city_names=self.city_names,
            state_codes=self.state_codes,
            active=self.active,
        )
        territory.split_rates = [rate.to_orm_model() for rate in self.split_rates]
        return territory
