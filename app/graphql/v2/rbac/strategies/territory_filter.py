from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_manager import TerritoryManager
from sqlalchemy import ColumnElement, Select, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class TerritoryFilterStrategy(RbacFilterStrategy):
    def __init__(
        self,
        resource: RbacResourceEnum,
        territory_id_column: InstrumentedAttribute[UUID | None],
        created_by_column: InstrumentedAttribute[UUID] | None = None,
    ) -> None:
        super().__init__()
        self._resource = resource
        self._territory_id_column = territory_id_column
        self._created_by_column = created_by_column

    @property
    def resource(self) -> RbacResourceEnum:
        return self._resource

    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        managed_territories = select(TerritoryManager.territory_id).where(
            TerritoryManager.user_id == user_id
        )

        child_territories = select(Territory.id).where(
            Territory.parent_id.in_(managed_territories)
        )

        grandchild_territories = select(Territory.id).where(
            Territory.parent_id.in_(child_territories)
        )

        conditions: list[ColumnElement[bool]] = [
            self._territory_id_column.in_(managed_territories),
            self._territory_id_column.in_(child_territories),
            self._territory_id_column.in_(grandchild_territories),
        ]

        if self._created_by_column is not None:
            conditions.append(self._created_by_column == user_id)

        return stmt.where(or_(*conditions))
