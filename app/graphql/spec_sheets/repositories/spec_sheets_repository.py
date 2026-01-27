"""Repository for SpecSheets entity with specific database operations."""

from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.db.v6.files import File
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


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

    async def create(self, entity: SpecSheet) -> SpecSheet:
        """
        Create a new spec sheet and eagerly load relationships.

        Overrides base create to ensure created_by relationship is loaded.

        Args:
            entity: SpecSheet to create

        Returns:
            Created SpecSheet with relationships loaded
        """
        created = await super().create(entity)

        # Refresh to load the created_by relationship
        stmt = (
            select(SpecSheet)
            .where(SpecSheet.id == created.id)
            .options(joinedload(SpecSheet.created_by))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

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
            stmt = stmt.where(SpecSheet.published.is_(True))

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
            stmt = stmt.where(SpecSheet.published.is_(True))

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

    async def move_to_folder(
        self,
        spec_sheet_id: UUID,
        folder_id: UUID | None,
    ) -> SpecSheet | None:
        """
        Move a spec sheet to a different folder by updating File.folder_id.

        Args:
            spec_sheet_id: UUID of the spec sheet
            folder_id: UUID of the target folder (None for root/no folder)

        Returns:
            Updated SpecSheet if found, None otherwise
        """
        spec_sheet = await self.get_by_id(spec_sheet_id)
        if not spec_sheet or not spec_sheet.file_id:
            return None

        # Update the File's folder_id
        file_stmt = select(File).where(File.id == spec_sheet.file_id)
        file_result = await self.session.execute(file_stmt)
        file = file_result.scalar_one_or_none()

        if file:
            file.folder_id = folder_id
            await self.session.flush()

        return spec_sheet

    async def find_by_folder(
        self,
        factory_id: UUID,
        folder_id: UUID | None,
        published_only: bool = True,
    ) -> list[SpecSheet]:
        """
        Find all spec sheets in a specific folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder (None for root/unassigned)
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models in the folder
        """
        stmt = (
            select(SpecSheet)
            .join(File, File.id == SpecSheet.file_id)
            .where(SpecSheet.factory_id == factory_id)
        )

        if folder_id is None:
            stmt = stmt.where(
                or_(
                    File.folder_id.is_(None),
                    SpecSheet.file_id.is_(None),
                )
            )
        else:
            stmt = stmt.where(File.folder_id == folder_id)

        if published_only:
            stmt = stmt.where(SpecSheet.published.is_(True))

        stmt = stmt.order_by(SpecSheet.display_name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
