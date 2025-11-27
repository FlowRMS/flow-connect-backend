"""Protocol defining the interface for repositories that support landing pages."""

from typing import Any, Protocol, runtime_checkable

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class LandingRepositoryProtocol(Protocol):
    """Protocol for repositories that support landing page queries."""

    session: AsyncSession
    model_class: type[Any]
    landing_model: type[Any]

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        ...
