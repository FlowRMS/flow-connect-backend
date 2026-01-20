"""Repository for spec sheet folder mutation operations."""

from uuid import UUID

from commons.db.v6.crm.spec_sheets import SpecSheet, SpecSheetFolder
from commons.db.v6.files import File, Folder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .folder_queries_repository import FolderQueriesRepository


class FolderMutationsRepository:
    """Repository for spec sheet folder mutation operations."""

    def __init__(self, session: AsyncSession, queries: FolderQueriesRepository) -> None:
        """Initialize the repository."""
        self.session = session
        self.queries = queries

    async def create_folder(
        self,
        factory_id: UUID,
        name: str,
        created_by_id: UUID,
        parent_id: UUID | None = None,
    ) -> Folder:
        """
        Create a new folder in pyfiles.folders and map it to the factory.

        Args:
            factory_id: UUID of the factory
            name: Name of the folder
            created_by_id: UUID of the user creating the folder
            parent_id: Optional parent folder ID

        Returns:
            Created Folder
        """
        if parent_id:
            parent_mapping = await self.queries.get_mapping(factory_id, parent_id)
            if not parent_mapping:
                raise ValueError(
                    f"Parent folder {parent_id} does not belong to factory {factory_id}"
                )

        folder = Folder(
            name=name,
            parent_id=parent_id,
        )
        folder.created_by_id = created_by_id
        self.session.add(folder)
        await self.session.flush()

        mapping = SpecSheetFolder(
            factory_id=factory_id,
            pyfiles_folder_id=folder.id,
        )
        self.session.add(mapping)
        await self.session.flush()

        return folder

    async def rename_folder(
        self, factory_id: UUID, folder_id: UUID, new_name: str
    ) -> Folder:
        """
        Rename a folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder to rename
            new_name: New name for the folder

        Returns:
            Updated Folder
        """
        mapping = await self.queries.get_mapping(factory_id, folder_id)
        if not mapping:
            raise ValueError(
                f"Folder {folder_id} does not belong to factory {factory_id}"
            )

        folder = await self.queries.find_by_id(folder_id)
        if not folder:
            raise ValueError(f"Folder {folder_id} not found")

        folder.name = new_name
        await self.session.flush()
        return folder

    async def delete_folder(self, factory_id: UUID, folder_id: UUID) -> bool:
        """
        Delete a folder only if it has no spec sheets and no subfolders.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If folder has spec sheets or subfolders
        """
        mapping = await self.queries.get_mapping(factory_id, folder_id)
        if not mapping:
            raise ValueError(
                f"Folder {folder_id} does not belong to factory {factory_id}"
            )

        subfolder_stmt = (
            select(func.count())
            .select_from(Folder)
            .where(Folder.parent_id == folder_id)
            .where(Folder.archived.is_(False))
        )
        subfolder_result = await self.session.execute(subfolder_stmt)
        subfolder_count = subfolder_result.scalar_one()

        if subfolder_count > 0:
            raise ValueError(
                f"Cannot delete folder: it contains {subfolder_count} subfolder(s). "
                "Delete or move the subfolders first."
            )

        spec_count_stmt = (
            select(func.count())
            .select_from(SpecSheet)
            .join(File, File.id == SpecSheet.file_id)
            .where(SpecSheet.factory_id == factory_id)
            .where(File.folder_id == folder_id)
        )
        spec_result = await self.session.execute(spec_count_stmt)
        spec_count = spec_result.scalar_one()

        if spec_count > 0:
            raise ValueError(
                f"Cannot delete folder: it contains {spec_count} spec sheet(s)"
            )

        await self.session.delete(mapping)

        folder = await self.queries.find_by_id(folder_id)
        if folder:
            folder.archived = True
            await self.session.flush()

        return True

    async def move_folder(
        self,
        factory_id: UUID,
        folder_id: UUID,
        new_parent_id: UUID | None,
    ) -> Folder:
        """
        Move a folder to a new parent.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder to move
            new_parent_id: New parent folder ID (None for root)

        Returns:
            Updated Folder
        """
        mapping = await self.queries.get_mapping(factory_id, folder_id)
        if not mapping:
            raise ValueError(
                f"Folder {folder_id} does not belong to factory {factory_id}"
            )

        if new_parent_id:
            parent_mapping = await self.queries.get_mapping(factory_id, new_parent_id)
            if not parent_mapping:
                raise ValueError(
                    f"Target parent folder {new_parent_id} does not belong to factory {factory_id}"
                )

            if folder_id == new_parent_id:
                raise ValueError("Cannot move folder into itself")

            current = await self.queries.find_by_id_with_relations(new_parent_id)
            while current and current.parent_id:
                if current.parent_id == folder_id:
                    raise ValueError("Cannot move folder into its own descendant")
                current = await self.queries.find_by_id(current.parent_id)

        folder = await self.queries.find_by_id(folder_id)
        if not folder:
            raise ValueError(f"Folder {folder_id} not found")

        folder.parent_id = new_parent_id
        await self.session.flush()
        return folder

    async def ensure_folder_exists(
        self,
        factory_id: UUID,
        folder_id: UUID,
    ) -> Folder | None:
        """
        Ensure a folder mapping exists for the factory.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the pyfiles.folder

        Returns:
            The Folder if mapping exists or created, None if folder doesn't exist
        """
        mapping = await self.queries.get_mapping(factory_id, folder_id)
        if mapping:
            return await self.queries.find_by_id(folder_id)

        folder = await self.queries.find_by_id(folder_id)
        if not folder:
            return None

        new_mapping = SpecSheetFolder(
            factory_id=factory_id,
            pyfiles_folder_id=folder_id,
        )
        self.session.add(new_mapping)
        await self.session.flush()

        return folder
