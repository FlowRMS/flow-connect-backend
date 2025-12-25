from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.crm.quotes import Quote, QuoteDetail, QuoteInsideRep, QuoteSplitRate
from sqlalchemy import Select, or_, select

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class QuoteOwnerFilterStrategy(RbacFilterStrategy):
    """
    Filter quotes by ownership through multiple paths.

    User can view quotes where they are:
    1. The creator (created_by_id)
    2. An inside rep (user_id in QuoteInsideRep)
    3. Assigned to any line item split rate (user_id in QuoteSplitRate)
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
        split_rate_subq = (
            select(QuoteDetail.quote_id)
            .join(QuoteSplitRate, QuoteSplitRate.quote_detail_id == QuoteDetail.id)
            .where(QuoteSplitRate.user_id == user_id)
            .distinct()
            .scalar_subquery()
        )

        inside_rep_subq = (
            select(QuoteInsideRep.quote_id)
            .where(QuoteInsideRep.user_id == user_id)
            .distinct()
            .scalar_subquery()
        )

        return stmt.where(
            or_(
                Quote.created_by_id == user_id,
                Quote.id.in_(split_rate_subq),
                Quote.id.in_(inside_rep_subq),
            )
        )
