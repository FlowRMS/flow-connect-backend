from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_type_enum import (
    TerritoryTypeEnum,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.territories.strawberry.territory_split_rate_response import (
    TerritorySplitRateResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class TerritoryLiteResponse(DTOMixin[Territory]):
    _instance: strawberry.Private[Territory]
    id: UUID
    name: str
    code: str
    territory_type: TerritoryTypeEnum
    parent_id: UUID | None
    active: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: Territory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            code=model.code,
            territory_type=model.territory_type,
            parent_id=model.parent_id,
            active=model.active,
            created_at=model.created_at,
        )


@strawberry.type
class TerritoryResponse(TerritoryLiteResponse):
    zip_codes: list[str]
    county_codes: list[str]
    city_names: list[str]
    state_codes: list[str]

    @classmethod
    def from_orm_model(cls, model: Territory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            code=model.code,
            territory_type=model.territory_type,
            parent_id=model.parent_id,
            active=model.active,
            created_at=model.created_at,
            zip_codes=model.zip_codes or [],
            county_codes=model.county_codes or [],
            city_names=model.city_names or [],
            state_codes=model.state_codes or [],
        )

    @strawberry.field
    def parent(self) -> TerritoryLiteResponse | None:
        parent = self._instance.parent
        if not parent:
            return None
        return TerritoryLiteResponse.from_orm_model(parent)

    @strawberry.field
    def split_rates(self) -> list[TerritorySplitRateResponse]:
        return TerritorySplitRateResponse.from_orm_model_list(
            self._instance.split_rates
        )

    @strawberry.field
    def managers(self) -> list[UserResponse]:
        return [
            UserResponse.from_orm_model(manager.user)
            for manager in self._instance.managers
        ]
