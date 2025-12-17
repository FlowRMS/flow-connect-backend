"""Repository for SpecSheet Highlights with specific database operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.spec_sheets.models.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
    SpecSheetHighlightVersion,
)


class SpecSheetHighlightsRepository(BaseRepository[SpecSheetHighlightVersion]):
    """
    Repository for SpecSheetHighlightVersion entity.

    Manages highlight versions and their regions.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the highlights repository.

        Args:
            context_wrapper: Context wrapper for user information
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, SpecSheetHighlightVersion)

    async def find_by_spec_sheet(
        self, spec_sheet_id: UUID, active_only: bool = False
    ) -> list[SpecSheetHighlightVersion]:
        """
        Find all highlight versions for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
            active_only: If True, only return active versions

        Returns:
            List of SpecSheetHighlightVersion models with regions loaded
        """
        stmt = (
            select(SpecSheetHighlightVersion)
            .options(selectinload(SpecSheetHighlightVersion.regions))
            .where(SpecSheetHighlightVersion.spec_sheet_id == spec_sheet_id)
            .order_by(SpecSheetHighlightVersion.version_number.desc())
        )

        if active_only:
            stmt = stmt.where(SpecSheetHighlightVersion.is_active == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_version_with_regions(
        self, version_id: UUID
    ) -> SpecSheetHighlightVersion | None:
        """
        Get a highlight version with all its regions.

        Args:
            version_id: UUID of the version

        Returns:
            SpecSheetHighlightVersion with regions or None
        """
        stmt = (
            select(SpecSheetHighlightVersion)
            .options(selectinload(SpecSheetHighlightVersion.regions))
            .where(SpecSheetHighlightVersion.id == version_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_next_version_number(self, spec_sheet_id: UUID) -> int:
        """
        Get the next version number for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet

        Returns:
            Next version number (max + 1)
        """
        stmt = select(func.max(SpecSheetHighlightVersion.version_number)).where(
            SpecSheetHighlightVersion.spec_sheet_id == spec_sheet_id
        )

        result = await self.session.execute(stmt)
        max_version = result.scalar_one_or_none()

        return (max_version or 0) + 1

    async def create_version_with_regions(
        self,
        spec_sheet_id: UUID,
        name: str,
        description: str | None,
        regions_data: list[dict],
    ) -> SpecSheetHighlightVersion:
        """
        Create a new highlight version with regions.

        Args:
            spec_sheet_id: UUID of the spec sheet
            name: Version name
            description: Optional description
            regions_data: List of region dictionaries

        Returns:
            Created SpecSheetHighlightVersion with regions
        """
        # Get next version number
        version_number = await self.get_next_version_number(spec_sheet_id)

        # Create version
        version = SpecSheetHighlightVersion(
            spec_sheet_id=spec_sheet_id,
            name=name,
            description=description,
            version_number=version_number,
            is_active=True,
        )
        # Set created_by_id after creation (init=False in mixin)
        version.created_by_id = self.context.auth_info.flow_user_id

        self.session.add(version)
        await self.session.flush()  # Get the version ID

        # Create regions
        for region_data in regions_data:
            region = SpecSheetHighlightRegion(
                version_id=version.id,
                page_number=region_data["page_number"],
                x=region_data["x"],
                y=region_data["y"],
                width=region_data["width"],
                height=region_data["height"],
                shape_type=region_data["shape_type"],
                color=region_data["color"],
                annotation=region_data.get("annotation"),
            )
            self.session.add(region)

        await self.session.flush()

        # Reload with regions - version was just created so it must exist
        result = await self.get_version_with_regions(version.id)
        assert result is not None
        return result

    async def update_version_regions(
        self, version_id: UUID, regions_data: list[dict]
    ) -> SpecSheetHighlightVersion | None:
        """
        Replace all regions in a version with new ones.

        Args:
            version_id: UUID of the version
            regions_data: New list of region dictionaries

        Returns:
            Updated version with new regions
        """
        version = await self.get_version_with_regions(version_id)
        if not version:
            return None

        # Delete existing regions
        for region in version.regions:
            await self.session.delete(region)

        # Create new regions
        for region_data in regions_data:
            region = SpecSheetHighlightRegion(
                version_id=version.id,
                page_number=region_data["page_number"],
                x=region_data["x"],
                y=region_data["y"],
                width=region_data["width"],
                height=region_data["height"],
                shape_type=region_data["shape_type"],
                color=region_data["color"],
                annotation=region_data.get("annotation"),
            )
            self.session.add(region)

        await self.session.flush()

        return await self.get_version_with_regions(version_id)

    async def delete_version(self, version_id: UUID) -> bool:
        """
        Delete a highlight version and all its regions.

        Args:
            version_id: UUID of the version

        Returns:
            True if deleted, False if not found
        """
        version = await self.get_by_id(version_id)
        if not version:
            return False

        await self.session.delete(version)
        await self.session.flush()
        return True

    async def count_regions_by_spec_sheet(self, spec_sheet_id: UUID) -> int:
        """
        Count total regions across all versions of a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet

        Returns:
            Total number of regions
        """
        stmt = (
            select(func.count(SpecSheetHighlightRegion.id))
            .join(SpecSheetHighlightVersion)
            .where(SpecSheetHighlightVersion.spec_sheet_id == spec_sheet_id)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0
