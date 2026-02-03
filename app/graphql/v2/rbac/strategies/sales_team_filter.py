from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core.sales_teams.sales_team import SalesTeam
from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from sqlalchemy import ColumnElement, Select, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class SalesTeamFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for SALES_MANAGER role visibility.

    Allows sales managers to see:
    1. Their own records (created_by_id = user_id)
    2. Records created by members of teams they manage
    """

    def __init__(
        self,
        resource: RbacResourceEnum,
        created_by_column: InstrumentedAttribute[UUID],
    ) -> None:
        super().__init__()
        self._resource = resource
        self._created_by_column = created_by_column

    @property
    def resource(self) -> RbacResourceEnum:
        return self._resource

    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        # Get all teams where user is the manager
        managed_teams = select(SalesTeam.id).where(SalesTeam.manager_id == user_id)

        # Get all user IDs in those managed teams
        team_member_user_ids = select(SalesTeamMember.user_id).where(
            SalesTeamMember.sales_team_id.in_(managed_teams)
        )

        conditions: list[ColumnElement[bool]] = [
            # User's own records
            self._created_by_column == user_id,
            # Records created by team members
            self._created_by_column.in_(team_member_user_ids),
        ]

        return stmt.where(or_(*conditions))
