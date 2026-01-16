from uuid import UUID

from commons.db.v6.crm.spec_sheets import SpecSheet, SpecSheetFolder
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FoldersRepository(BaseRepository[SpecSheetFolder]):
    """
    Repository for Folder entity.

    Manages folder persistence for organizing spec sheets.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """Initialize the Folders repository."""
        super().__init__(session, context_wrapper, SpecSheetFolder)

    async def find_by_factory(self, factory_id: UUID) -> list[SpecSheetFolder]:
        """
        Find all folders for a given factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of Folder models
        """
        stmt = (
            select(SpecSheetFolder)
            .where(SpecSheetFolder.factory_id == factory_id)
            .order_by(SpecSheetFolder.folder_path)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_factory_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[SpecSheetFolder, int]]:
        """
        Find all folders for a given factory with spec sheet counts.

        Uses a subquery to count spec sheets in each folder efficiently.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (Folder, spec_sheet_count)
        """
        # Subquery to count spec sheets per folder_path
        count_subquery = (
            select(
                SpecSheet.folder_path,
                func.count().label("spec_count"),
            )
            .where(SpecSheet.factory_id == factory_id)
            .group_by(SpecSheet.folder_path)
            .subquery()
        )

        # Main query joining folders with counts
        stmt = (
            select(
                SpecSheetFolder,
                func.coalesce(count_subquery.c.spec_count, 0).label("spec_count"),
            )
            .outerjoin(
                count_subquery,
                SpecSheetFolder.folder_path == count_subquery.c.folder_path,
            )
            .where(SpecSheetFolder.factory_id == factory_id)
            .order_by(SpecSheetFolder.folder_path)
        )

        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_folder_paths_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[str, int]]:
        """
        Get all folder paths with their spec sheet counts.

        This includes:
        1. Folders from spec_sheet_folders table (including empty folders)
        2. Virtual folders derived from spec_sheets.folder_path

        Counts are recursive (parent folders include counts from subfolders).

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (folder_path, spec_sheet_count) ordered by path
        """
        # Get all spec sheets with their folder_paths for this factory
        spec_stmt = select(SpecSheet.folder_path).where(
            and_(
                SpecSheet.factory_id == factory_id,
                SpecSheet.folder_path.isnot(None),
                SpecSheet.folder_path != "",
            )
        )
        spec_result = await self.session.execute(spec_stmt)
        spec_folder_paths = [row[0] for row in spec_result.all()]

        # Also get all folders from spec_sheet_folders table (including empty ones)
        folder_stmt = select(SpecSheetFolder.folder_path).where(
            SpecSheetFolder.factory_id == factory_id
        )
        folder_result = await self.session.execute(folder_stmt)
        explicit_folders = [row[0] for row in folder_result.all()]

        # Build a set of all folder paths (including parent paths)
        all_paths: set[str] = set()
        path_counts: dict[str, int] = {}

        # Add paths from spec sheets and count them
        for folder_path in spec_folder_paths:
            # Add count for the exact folder
            path_counts[folder_path] = path_counts.get(folder_path, 0) + 1

            # Add all parent paths to the set
            parts = folder_path.split("/")
            for i in range(1, len(parts) + 1):
                parent_path = "/".join(parts[:i])
                all_paths.add(parent_path)

        # Add explicit folders from spec_sheet_folders table (even if empty)
        for folder_path in explicit_folders:
            all_paths.add(folder_path)
            # Also add parent paths for consistency
            parts = folder_path.split("/")
            for i in range(1, len(parts) + 1):
                parent_path = "/".join(parts[:i])
                all_paths.add(parent_path)

        # Calculate recursive counts for each path
        result_list: list[tuple[str, int]] = []
        for path in sorted(all_paths):
            # Count all spec sheets in this path and subpaths
            count = sum(
                c
                for p, c in path_counts.items()
                if p == path or p.startswith(f"{path}/")
            )
            result_list.append((path, count))

        return result_list

    async def find_by_path(
        self, factory_id: UUID, folder_path: str
    ) -> SpecSheetFolder | None:
        """
        Find a folder by its exact path.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path

        Returns:
            Folder if found, None otherwise
        """
        stmt = select(SpecSheetFolder).where(
            and_(
                SpecSheetFolder.factory_id == factory_id,
                SpecSheetFolder.folder_path == folder_path,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_folder(
        self, factory_id: UUID, folder_path: str
    ) -> SpecSheetFolder:
        """
        Create a new folder.

        Also creates any parent folders that don't exist.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path (e.g., "Folder1/Folder2")

        Returns:
            Created Folder
        """
        # Create parent folders if they don't exist
        parts = folder_path.split("/")
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            existing = await self.find_by_path(factory_id, current_path)

            if not existing:
                folder = SpecSheetFolder(
                    factory_id=factory_id, folder_path=current_path
                )
                _ = await self.create(folder)

        # Return the final (deepest) folder
        result = await self.find_by_path(factory_id, folder_path)
        if result is None:
            raise ValueError(f"Failed to create folder: {folder_path}")
        return result

    async def rename_folder(
        self, factory_id: UUID, old_path: str, new_name: str
    ) -> tuple[SpecSheetFolder, int]:
        """
        Rename a folder and update all spec sheets in it.

        Args:
            factory_id: UUID of the factory
            old_path: Current folder path
            new_name: New name for the folder (just the name, not full path)

        Returns:
            Tuple of (updated Folder, number of spec sheets updated)
        """
        # Calculate the new path
        path_parts = old_path.split("/")
        path_parts[-1] = new_name
        new_path = "/".join(path_parts)

        # Update all folders with this path prefix
        stmt = select(SpecSheetFolder).where(
            and_(
                SpecSheetFolder.factory_id == factory_id,
                or_(
                    SpecSheetFolder.folder_path == old_path,
                    SpecSheetFolder.folder_path.like(f"{old_path}/%"),
                ),
            )
        )
        result = await self.session.execute(stmt)
        folders = list(result.scalars().all())

        for folder in folders:
            if folder.folder_path == old_path:
                folder.folder_path = new_path
            else:
                # Update nested folders
                suffix = folder.folder_path[len(old_path) :]
                folder.folder_path = new_path + suffix

        # Update all spec sheets with this path prefix
        spec_stmt = select(SpecSheet).where(
            and_(
                SpecSheet.factory_id == factory_id,
                or_(
                    SpecSheet.folder_path == old_path,
                    SpecSheet.folder_path.like(f"{old_path}/%"),
                ),
            )
        )
        spec_result = await self.session.execute(spec_stmt)
        spec_sheets = list(spec_result.scalars().all())

        spec_count = 0
        for spec_sheet in spec_sheets:
            if spec_sheet.folder_path == old_path:
                spec_sheet.folder_path = new_path
            elif spec_sheet.folder_path:
                suffix = spec_sheet.folder_path[len(old_path) :]
                spec_sheet.folder_path = new_path + suffix
            spec_count += 1

        await self.session.flush()

        # Return the updated folder (or create it if it doesn't exist)
        updated_folder = await self.find_by_path(factory_id, new_path)
        if updated_folder is None:
            # Folder didn't exist in folders table, create it now
            updated_folder = await self.create_folder(factory_id, new_path)
        return updated_folder, spec_count

    async def delete_folder(self, factory_id: UUID, folder_path: str) -> bool:
        """
        Delete a folder only if it has no spec sheets and no subfolders.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path to delete

        Returns:
            True if deleted, False if folder has spec sheets or subfolders

        Raises:
            ValueError: If folder has spec sheets or subfolders and cannot be deleted
        """
        # Check if any subfolders exist
        subfolder_stmt = (
            select(func.count())
            .select_from(SpecSheetFolder)
            .where(
                and_(
                    SpecSheetFolder.factory_id == factory_id,
                    SpecSheetFolder.folder_path.like(f"{folder_path}/%"),
                )
            )
        )
        subfolder_result = await self.session.execute(subfolder_stmt)
        subfolder_count = subfolder_result.scalar_one()

        if subfolder_count > 0:
            raise ValueError(
                f"Cannot delete folder '{folder_path}': it contains {subfolder_count} subfolder(s). "
                "Delete or move the subfolders first."
            )

        # Check if any spec sheets exist in this folder
        count_stmt = (
            select(func.count())
            .select_from(SpecSheet)
            .where(
                and_(
                    SpecSheet.factory_id == factory_id,
                    SpecSheet.folder_path == folder_path,
                )
            )
        )
        count_result = await self.session.execute(count_stmt)
        spec_count = count_result.scalar_one()

        if spec_count > 0:
            raise ValueError(
                f"Cannot delete folder '{folder_path}': it contains {spec_count} spec sheet(s)"
            )

        # Delete only this folder (no subfolders since we validated above)
        folder = await self.find_by_path(factory_id, folder_path)
        if folder:
            await self.session.delete(folder)
            await self.session.flush()

        return True

    async def get_spec_sheet_count(self, factory_id: UUID, folder_path: str) -> int:
        """
        Get the count of spec sheets in a folder (not including subfolders).

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path

        Returns:
            Number of spec sheets in the folder
        """
        stmt = (
            select(func.count())
            .select_from(SpecSheet)
            .where(
                and_(
                    SpecSheet.factory_id == factory_id,
                    SpecSheet.folder_path == folder_path,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def ensure_folder_exists(
        self, factory_id: UUID, folder_path: str
    ) -> SpecSheetFolder:
        """
        Ensure a folder exists, creating it if necessary.

        This is used when uploading a spec sheet to ensure the folder hierarchy exists.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path

        Returns:
            The existing or created Folder
        """
        existing = await self.find_by_path(factory_id, folder_path)
        if existing:
            return existing
        return await self.create_folder(factory_id, folder_path)

    async def move_folder(
        self, factory_id: UUID, old_path: str, new_path: str
    ) -> tuple[int, int]:
        """
        Move a folder to a new location.

        Updates the folder_path of all folders and spec sheets.

        Args:
            factory_id: UUID of the factory
            old_path: Current folder path (e.g., "F1/F2/F3/ultimo2")
            new_path: New folder path (e.g., "ultimo2" for root level)

        Returns:
            Tuple of (folders updated, spec sheets updated)
        """
        # Update all folders with this path prefix
        folder_stmt = select(SpecSheetFolder).where(
            and_(
                SpecSheetFolder.factory_id == factory_id,
                or_(
                    SpecSheetFolder.folder_path == old_path,
                    SpecSheetFolder.folder_path.like(f"{old_path}/%"),
                ),
            )
        )
        folder_result = await self.session.execute(folder_stmt)
        folders = list(folder_result.scalars().all())

        folder_count = 0
        for folder in folders:
            if folder.folder_path == old_path:
                folder.folder_path = new_path
            else:
                # Update nested folders
                suffix = folder.folder_path[len(old_path) :]
                folder.folder_path = new_path + suffix
            folder_count += 1

        # Update all spec sheets with this path prefix
        spec_stmt = select(SpecSheet).where(
            and_(
                SpecSheet.factory_id == factory_id,
                or_(
                    SpecSheet.folder_path == old_path,
                    SpecSheet.folder_path.like(f"{old_path}/%"),
                ),
            )
        )
        spec_result = await self.session.execute(spec_stmt)
        spec_sheets = list(spec_result.scalars().all())

        spec_count = 0
        for spec_sheet in spec_sheets:
            if spec_sheet.folder_path == old_path:
                spec_sheet.folder_path = new_path
            elif spec_sheet.folder_path:
                suffix = spec_sheet.folder_path[len(old_path) :]
                spec_sheet.folder_path = new_path + suffix
            spec_count += 1

        # Ensure new path hierarchy exists
        if new_path:
            _ = await self.ensure_folder_exists(factory_id, new_path)

        await self.session.flush()
        return folder_count, spec_count
