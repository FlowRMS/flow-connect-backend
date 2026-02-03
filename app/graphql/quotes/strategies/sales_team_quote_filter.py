from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core.sales_teams.sales_team import SalesTeam
from commons.db.v6.core.sales_teams.sales_team_member import SalesTeamMember
from commons.db.v6.crm.quotes import Quote, QuoteDetail, QuoteInsideRep, QuoteSplitRate
from sqlalchemy import Select, or_, select

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class SalesTeamQuoteFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for SALES_MANAGER role on quotes.

    Allows sales managers to see quotes where:
    1. They created the quote
    2. They are in split rates or inside reps
    3. A team member they manage created the quote
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

        # Get all user IDs in those managed teams (includes the manager's team members)
        team_member_user_ids = select(SalesTeamMember.user_id).where(
            SalesTeamMember.sales_team_id.in_(managed_teams)
        )

        # Quotes where user or team members are in split rates
        split_rate_subq = (
            select(QuoteDetail.quote_id)
            .join(QuoteSplitRate, QuoteSplitRate.quote_detail_id == QuoteDetail.id)
            .where(
                or_(
                    QuoteSplitRate.user_id == user_id,
                    QuoteSplitRate.user_id.in_(team_member_user_ids),
                )
            )
            .distinct()
            .scalar_subquery()
        )

        # Quotes where user or team members are in inside reps
        inside_rep_subq = (
            select(QuoteDetail.quote_id)
            .join(QuoteInsideRep, QuoteInsideRep.quote_detail_id == QuoteDetail.id)
            .where(
                or_(
                    QuoteInsideRep.user_id == user_id,
                    QuoteInsideRep.user_id.in_(team_member_user_ids),
                )
            )
            .distinct()
            .scalar_subquery()
        )

        return stmt.where(
            or_(
                # User's own quotes
                Quote.created_by_id == user_id,
                # Team members' quotes
                Quote.created_by_id.in_(team_member_user_ids),
                # Quotes where user/team members are in split rates
                Quote.id.in_(split_rate_subq),
                # Quotes where user/team members are inside reps
                Quote.id.in_(inside_rep_subq),
            )
        )
