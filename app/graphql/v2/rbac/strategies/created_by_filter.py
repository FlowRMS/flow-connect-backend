from typing import Any, Protocol
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from sqlalchemy import Select
from sqlalchemy.orm import Mapped

from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class HasCreatedById(Protocol):
    """Protocol for models with a created_by_id column."""

    created_by_id: Mapped[UUID]


class CreatedByFilterStrategy(RbacFilterStrategy):
    """
    Filter strategy for entities with a simple created_by_id column.

    Use this for entities like Products where ownership is determined
    solely by who created the record.
    """

    def __init__(
        self, resource: RbacResourceEnum, model_class: type[HasCreatedById]
    ) -> None:
        super().__init__()
        self._resource = resource
        self._model_class = model_class

    @property
    def resource(self) -> RbacResourceEnum:
        return self._resource

    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        return stmt.where(self._model_class.created_by_id == user_id)  # type: ignore[arg-type]
