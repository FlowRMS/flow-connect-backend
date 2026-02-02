from uuid import UUID

import strawberry
from commons.db.v6.core.sales_teams.sales_team import SalesTeam

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class SalesTeamInput(BaseInputGQL[SalesTeam]):
    name: str
    manager_id: UUID
    territory_id: UUID | None = None
    active: bool = True

    def to_orm_model(self) -> SalesTeam:
        return SalesTeam(
            name=self.name,
            manager_id=self.manager_id,
            territory_id=self.territory_id,
            active=self.active,
        )


@strawberry.input
class SalesTeamMemberInput:
    user_id: UUID
    position: int = 0
