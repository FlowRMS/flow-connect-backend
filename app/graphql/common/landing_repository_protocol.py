from typing import Any, Protocol, runtime_checkable

from commons.db.v6 import RbacResourceEnum
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class LandingRepositoryProtocol(Protocol):
    """Protocol for repositories that support landing page queries."""

    session: AsyncSession
    model_class: type[Any]
    landing_model: type[Any]
    rbac_resource: RbacResourceEnum | None

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for landing page.

        The returned statement should include a 'user_ids' column as a
        PostgreSQL array containing all user UUIDs that "own" this record
        for RBAC filtering purposes.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        ...
