from typing import Any, Protocol
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from sqlalchemy import Select
from sqlalchemy.orm import Mapped

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class HasUserId(Protocol):
    """Protocol for split rate models with a user_id column."""

    user_id: Mapped[UUID]


class SplitRateFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for entities with ownership through split rates.

    Use this for entities like Orders where the split rate table is already
    joined in the statement. Filters by checking if the user_id on the
    split rate matches the current user.
    """

    def __init__(
        self,
        resource: RbacResourceEnum,
        split_rate_model: type[HasUserId],
    ) -> None:
        super().__init__()
        self._resource = resource
        self._split_rate_model = split_rate_model

    @property
    def resource(self) -> RbacResourceEnum:
        return self._resource

    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        return stmt.where(self._split_rate_model.user_id == user_id)
