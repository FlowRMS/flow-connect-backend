"""Repository for SpecSheets entity with specific database operations."""

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.spec_sheets.models.spec_sheet_model import SpecSheet


class SpecSheetsRepository(BaseRepository[SpecSheet]):
    """
    Repository for SpecSheets entity.

    Extends BaseRepository with spec sheet-specific query methods.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the SpecSheets repository.

        Args:
            context_wrapper: Context wrapper for user information
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, SpecSheet)

    async def find_by_manufacturer(
        self, manufacturer_id: UUID, published_only: bool = True
    ) -> list[SpecSheet]:
        """
        Find all spec sheets for a given manufacturer.

        Args:
            manufacturer_id: UUID of the manufacturer
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models
        """
        stmt = select(SpecSheet).where(SpecSheet.manufacturer_id == manufacturer_id)

        if published_only:
            stmt = stmt.where(SpecSheet.published == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_spec_sheets(
        self,
        search_term: str,
        manufacturer_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheet]:
        """
        Search spec sheets by term, manufacturer, and categories.

        Args:
            search_term: Term to search in display_name and file_name
            manufacturer_id: Optional manufacturer filter
            categories: Optional categories filter
            published_only: Filter only published spec sheets
            limit: Maximum number of results

        Returns:
            List of matching SpecSheet models
        """
        stmt = select(SpecSheet)

        # Search term filter
        if search_term:
            search_pattern = f"%{search_term}%"
            stmt = stmt.where(
                or_(
                    SpecSheet.display_name.ilike(search_pattern),
                    SpecSheet.file_name.ilike(search_pattern),
                )
            )

        # Manufacturer filter
        if manufacturer_id:
            stmt = stmt.where(SpecSheet.manufacturer_id == manufacturer_id)

        # Categories filter
        if categories:
            stmt = stmt.where(SpecSheet.categories.overlap(categories))

        # Published filter
        if published_only:
            stmt = stmt.where(SpecSheet.published == True)  # noqa: E712

        stmt = stmt.limit(limit).order_by(SpecSheet.display_name)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def increment_usage_count(self, spec_sheet_id: UUID) -> None:
        """
        Increment the usage count for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
        """
        spec_sheet = await self.get_by_id(spec_sheet_id)
        if spec_sheet:
            spec_sheet.usage_count += 1
            await self.session.commit()
