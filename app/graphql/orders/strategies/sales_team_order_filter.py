from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.commission.orders import (
    Order,
    OrderDetail,
    OrderInsideRep,
    OrderSplitRate,
)
from commons.db.v6.core.sales_teams.sales_team import SalesTeam
from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from sqlalchemy import Select, or_, select

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class SalesTeamOrderFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for SALES_MANAGER role on orders.

    Allows sales managers to see orders where:
    1. They created the order
    2. They are in split rates or inside reps
    3. A team member they manage created the order
    4. A team member they manage is in split rates or inside reps
    """

    def __init__(self, resource: RbacResourceEnum) -> None:
        super().__init__()
        self._resource = resource

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

        # Orders where user or team members are in split rates
        split_rate_subq = (
            select(OrderDetail.order_id)
            .join(OrderSplitRate, OrderSplitRate.order_detail_id == OrderDetail.id)
            .where(
                or_(
                    OrderSplitRate.user_id == user_id,
                    OrderSplitRate.user_id.in_(team_member_user_ids),
                )
            )
            .distinct()
            .scalar_subquery()
        )

        # Orders where user or team members are in inside reps
        inside_rep_subq = (
            select(OrderDetail.order_id)
            .join(OrderInsideRep, OrderInsideRep.order_detail_id == OrderDetail.id)
            .where(
                or_(
                    OrderInsideRep.user_id == user_id,
                    OrderInsideRep.user_id.in_(team_member_user_ids),
                )
            )
            .distinct()
            .scalar_subquery()
        )

        return stmt.where(
            or_(
                # User's own orders
                Order.created_by_id == user_id,
                # Team members' orders
                Order.created_by_id.in_(team_member_user_ids),
                # Orders where user/team members are in split rates
                Order.id.in_(split_rate_subq),
                # Orders where user/team members are inside reps
                Order.id.in_(inside_rep_subq),
            )
        )
