from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.sales_teams.sales_team import SalesTeam

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.sales_teams.strawberry.sales_team_member_response import (
    SalesTeamMemberResponse,
)
from app.graphql.v2.core.territories.strawberry.territory_response import (
    TerritoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SalesTeamResponse(DTOMixin[SalesTeam]):
    _instance: strawberry.Private[SalesTeam]
    id: UUID
    name: str
    manager_id: UUID
    territory_id: UUID | None
    active: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SalesTeam) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            manager_id=model.manager_id,
            territory_id=model.territory_id,
            active=model.active,
            created_at=model.created_at,
        )

    @strawberry.field
    def manager(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.manager)

    @strawberry.field
    def territory(self) -> TerritoryLiteResponse | None:
        if not self._instance.territory:
            return None
        return TerritoryLiteResponse.from_orm_model(self._instance.territory)

    @strawberry.field
    def members(self) -> list[SalesTeamMemberResponse]:
        return [
            SalesTeamMemberResponse(
                id=member.id,
                user_id=member.user_id,
                position=member.position,
                user=UserResponse.from_orm_model(member.user),
                created_at=member.created_at,
            )
            for member in self._instance.members
        ]
