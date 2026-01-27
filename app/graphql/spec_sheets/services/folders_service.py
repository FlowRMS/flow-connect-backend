from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.files import Folder

from app.graphql.spec_sheets.repositories.folder_mutations_repository import (
    FolderMutationsRepository,
)
from app.graphql.spec_sheets.repositories.folder_queries_repository import (
    FolderQueriesRepository,
)
from app.graphql.spec_sheets.repositories.folders_repository import FoldersRepository


class FoldersService:
    """Service for Folder entity business logic."""

    def __init__(
        self,
        repository: FoldersRepository,
        queries_repository: FolderQueriesRepository,
        mutations_repository: FolderMutationsRepository,
        auth_info: AuthInfo,
    ) -> None:
        """Initialize the Folders service."""
        super().__init__()
        self.repository = repository
        self.queries_repository = queries_repository
        self.mutations_repository = mutations_repository
        self.auth_info = auth_info

    async def get_folders_by_factory(self, factory_id: UUID) -> list[Folder]:
        """
        Get all pyfiles.folders for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of pyfiles.Folder models
        """
        return await self.queries_repository.find_by_factory(factory_id)

    async def get_folders_by_factory_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[Folder, int]]:
        """
        Get all folders for a factory with spec sheet counts.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (Folder, spec_sheet_count)
        """
        return await self.queries_repository.get_folders_with_hierarchy(factory_id)

    async def get_folder_paths_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[str, int]]:
        """
        Get all folder paths that contain spec sheets with their counts.

        This includes virtual folders derived from spec sheet folder_paths,
        not just folders in the spec_sheet_folders table. Counts are recursive.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (folder_path, spec_sheet_count)
        """
        return await self.repository.get_folder_paths_with_counts(factory_id)

    async def _find_folder_by_name_in_parent(
        self, factory_id: UUID, name: str, parent_id: UUID | None
    ) -> Folder | None:
        """
        Find a folder by name within a specific parent.

        Args:
            factory_id: UUID of the factory
            name: Folder name to find
            parent_id: Parent folder ID (None for root level)

        Returns:
            Folder if found, None otherwise
        """
        if parent_id is None:
            folders = await self.queries_repository.get_root_folders(factory_id)
        else:
            folders = await self.queries_repository.get_children(factory_id, parent_id)

        for folder in folders:
            if folder.name == name:
                return folder
        return None

    async def _resolve_parent_id_from_path(
        self, factory_id: UUID, parent_path: str
    ) -> UUID | None:
        """
        Resolve a parent folder ID from a path string.

        If the parent doesn't exist as a pyfiles.Folder, creates it.

        Args:
            factory_id: UUID of the factory
            parent_path: Parent folder path (empty string for root)

        Returns:
            Parent folder UUID or None if root level
        """
        if not parent_path:
            return None

        parts = parent_path.split("/")
        current_parent_id: UUID | None = None

        for part in parts:
            folder = await self._find_folder_by_name_in_parent(
                factory_id, part, current_parent_id
            )
            if folder:
                current_parent_id = folder.id
            else:
                # Create the missing parent folder
                new_folder = await self.mutations_repository.create_folder(
                    factory_id=factory_id,
                    name=part,
                    created_by_id=self.auth_info.flow_user_id,
                    parent_id=current_parent_id,
                )
                current_parent_id = new_folder.id

        return current_parent_id

    async def _resolve_folder_id_from_path(
        self, factory_id: UUID, folder_path: str
    ) -> UUID | None:
        """
        Resolve a folder ID from a path string.

        Args:
            factory_id: UUID of the factory
            folder_path: Full folder path

        Returns:
            Folder UUID or None if not found
        """
        if not folder_path:
            return None

        parts = folder_path.split("/")
        current_parent_id: UUID | None = None

        for part in parts:
            folder = await self._find_folder_by_name_in_parent(
                factory_id, part, current_parent_id
            )
            if folder:
                current_parent_id = folder.id
            else:
                return None  # Path doesn't exist

        return current_parent_id

    async def create_folder(self, factory_id: UUID, folder_path: str) -> Folder:
        """
        Create a new folder in pyfiles.folders (and any parent folders that don't exist).

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path (e.g., "Folder1/Folder2")

        Returns:
            Created pyfiles.Folder
        """
        parts = folder_path.split("/")
        folder_name = parts[-1]
        parent_path = "/".join(parts[:-1]) if len(parts) > 1 else ""

        parent_id = await self._resolve_parent_id_from_path(factory_id, parent_path)

        return await self.mutations_repository.create_folder(
            factory_id=factory_id,
            name=folder_name,
            created_by_id=self.auth_info.flow_user_id,
            parent_id=parent_id,
        )

    async def create_subfolder(
        self, factory_id: UUID, parent_path: str, folder_name: str
    ) -> Folder:
        """
        Create a new subfolder under a parent folder in pyfiles.folders.

        Args:
            factory_id: UUID of the factory
            parent_path: The parent folder path (empty string for root)
            folder_name: Name of the new folder

        Returns:
            Created pyfiles.Folder
        """
        parent_id = await self._resolve_parent_id_from_path(factory_id, parent_path)

        return await self.mutations_repository.create_folder(
            factory_id=factory_id,
            name=folder_name,
            created_by_id=self.auth_info.flow_user_id,
            parent_id=parent_id,
        )

    async def rename_folder(
        self, factory_id: UUID, folder_path: str, new_name: str
    ) -> tuple[Folder, int]:
        """
        Rename a folder in pyfiles.folders.

        Args:
            factory_id: UUID of the factory
            folder_path: Current folder path
            new_name: New name for the folder

        Returns:
            Tuple of (updated Folder, number of spec sheets updated - always 0 for pyfiles)
        """
        folder_id = await self._resolve_folder_id_from_path(factory_id, folder_path)
        if not folder_id:
            raise ValueError(f"Folder not found: {folder_path}")

        folder = await self.mutations_repository.rename_folder(
            factory_id=factory_id,
            folder_id=folder_id,
            new_name=new_name,
        )
        # pyfiles doesn't need to update spec sheets - they reference by folder_id
        return folder, 0

    async def delete_folder(self, factory_id: UUID, folder_path: str) -> bool:
        """
        Delete a folder from pyfiles.folders only if it has no spec sheets.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If folder has spec sheets and cannot be deleted
        """
        folder_id = await self._resolve_folder_id_from_path(factory_id, folder_path)
        if not folder_id:
            raise ValueError(f"Folder not found: {folder_path}")

        return await self.mutations_repository.delete_folder(
            factory_id=factory_id,
            folder_id=folder_id,
        )

    async def ensure_folder_exists(self, factory_id: UUID, folder_path: str) -> Folder:
        """
        Ensure a folder exists in pyfiles.folders, creating it if necessary.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path

        Returns:
            The existing or created pyfiles.Folder
        """
        folder_id = await self._resolve_folder_id_from_path(factory_id, folder_path)
        if folder_id:
            folder = await self.queries_repository.find_by_id(folder_id)
            if folder:
                return folder

        # Create the folder if it doesn't exist
        return await self.create_folder(factory_id, folder_path)
