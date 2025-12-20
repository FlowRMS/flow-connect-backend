from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from sqlalchemy import Select, or_
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class MultiOwnerFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for entities with multiple ownership columns.

    Use this for entities like Customers where ownership can be determined
    by multiple columns (e.g., created_by_id OR inside_rep_id).
    Columns can be simple UUID columns or ARRAY columns.
    """

    def __init__(
        self,
        resource: RbacResourceEnum,
        owner_columns: list[InstrumentedAttribute[Any]],
        *,
        array_columns: list[InstrumentedAttribute[Any]] | None = None,
    ) -> None:
        """
        Initialize the multi-owner filter strategy.

        Args:
            resource: The RBAC resource this strategy applies to
            owner_columns: List of UUID columns to check for ownership (using ==)
            array_columns: List of ARRAY columns to check for ownership (using contains())
        """
        super().__init__()
        self._resource = resource
        self._owner_columns = owner_columns
        self._array_columns = array_columns or []

    @property
    def resource(self) -> RbacResourceEnum:
        return self._resource

    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        conditions: list[Any] = []

        for column in self._owner_columns:
            conditions.append(column == user_id)

        for array_column in self._array_columns:
            conditions.append(array_column.contains([user_id]))

        if not conditions:
            return stmt

        if len(conditions) == 1:
            return stmt.where(conditions[0])

        return stmt.where(or_(*conditions))
