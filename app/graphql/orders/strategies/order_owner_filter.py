from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.commission.orders import (
    Order,
    OrderDetail,
    OrderInsideRep,
    OrderSplitRate,
)
from sqlalchemy import Select, or_, select

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class OrderOwnerFilterStrategy(RbacFilterStrategy):
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
            select(OrderDetail.order_id)
            .join(OrderSplitRate, OrderSplitRate.order_detail_id == OrderDetail.id)
            .where(OrderSplitRate.user_id == user_id)
            .distinct()
            .scalar_subquery()
        )

        inside_rep_subq = (
            select(OrderDetail.order_id)
            .join(OrderInsideRep, OrderInsideRep.order_detail_id == OrderDetail.id)
            .where(OrderInsideRep.user_id == user_id)
            .distinct()
            .scalar_subquery()
        )

        return stmt.where(
            or_(
                Order.created_by_id == user_id,
                Order.id.in_(split_rate_subq),
                Order.id.in_(inside_rep_subq),
            )
        )
