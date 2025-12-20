from abc import ABC, abstractmethod
from typing import Any, TypeVar
from uuid import UUID

from commons.db.v6 import RbacPrivilegeOptionEnum, RbacResourceEnum
from sqlalchemy import Select

from app.core.db.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class RbacFilterStrategy(ABC):
    """
    Abstract base class for RBAC filtering strategies.

    Each strategy defines how to filter a query based on user ownership.
    Subclasses implement resource-specific logic (e.g., created_by_id,
    user_owner_ids array, or multi-table relationships).
    """

    @property
    @abstractmethod
    def resource(self) -> RbacResourceEnum:
        """The RBAC resource this strategy applies to."""
        ...

    @abstractmethod
    def apply_ownership_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
    ) -> Select[tuple[Any, ...]]:
        """
        Apply ownership-based WHERE clause filtering to the statement.

        Called when user has OWN privilege (not ALL).

        Args:
            stmt: The base select statement to filter
            user_id: The current user's ID

        Returns:
            The filtered select statement
        """
        ...

    def apply_filter(
        self,
        stmt: Select[tuple[Any, ...]],
        user_id: UUID,
        privilege_option: RbacPrivilegeOptionEnum,
    ) -> Select[tuple[Any, ...]]:
        """
        Apply RBAC filtering based on privilege option.

        Args:
            stmt: The base select statement to filter
            user_id: The current user's ID
            privilege_option: OWN (filter by ownership) or ALL (no filter)

        Returns:
            The filtered select statement
        """
        if privilege_option == RbacPrivilegeOptionEnum.ALL:
            return stmt

        return self.apply_ownership_filter(stmt, user_id)
