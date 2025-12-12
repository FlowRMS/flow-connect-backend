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

    async def find_by_factory(
        self, factory_id: UUID, published_only: bool = True
    ) -> list[SpecSheet]:
        """
        Find all spec sheets for a given factory.

        Args:
            factory_id: UUID of the factory
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models
        """
        stmt = select(SpecSheet).where(SpecSheet.factory_id == factory_id)

        if published_only:
            stmt = stmt.where(SpecSheet.published == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_spec_sheets(
        self,
        search_term: str,
        factory_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheet]:
        """
        Search spec sheets by term, factory, and categories.

        Args:
            search_term: Term to search in display_name and file_name
            factory_id: Optional factory filter
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

        # Factory filter
        if factory_id:
            stmt = stmt.where(SpecSheet.factory_id == factory_id)

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

    async def update_folder_paths(
        self,
        factory_id: UUID,
        old_path: str,
        new_path: str,
    ) -> int:
        """
        Update folder paths for all spec sheets matching the old path.

        This updates both exact matches and nested paths.
        E.g., moving "Folder1/Folder2" to "Folder1" would update:
        - "Folder1/Folder2" -> "Folder2"
        - "Folder1/Folder2/Folder3" -> "Folder2/Folder3"

        Args:
            factory_id: UUID of the factory
            old_path: The current folder path prefix
            new_path: The new folder path (empty string for root level)

        Returns:
            Number of spec sheets updated
        """
        # Find all spec sheets with paths starting with old_path
        stmt = select(SpecSheet).where(
            SpecSheet.factory_id == factory_id,
            or_(
                SpecSheet.folder_path == old_path,
                SpecSheet.folder_path.like(f"{old_path}/%"),
            ),
        )

        result = await self.session.execute(stmt)
        spec_sheets = list(result.scalars().all())

        count = 0
        for spec_sheet in spec_sheets:
            if spec_sheet.folder_path == old_path:
                # Exact match - set to new path
                spec_sheet.folder_path = new_path if new_path else None
            else:
                # Nested path - replace prefix
                suffix = spec_sheet.folder_path[len(old_path) + 1 :]  # +1 for the /
                spec_sheet.folder_path = f"{new_path}/{suffix}" if new_path else suffix
            count += 1

        if count > 0:
            await self.session.commit()

        return count
