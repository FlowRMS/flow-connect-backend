"""Service for Folder entity business logic."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.spec_sheets import SpecSheetFolder

from app.graphql.spec_sheets.repositories.folders_repository import FoldersRepository


class FoldersService:
    """Service for Folder entity business logic."""

    def __init__(
        self,
        repository: FoldersRepository,
        auth_info: AuthInfo,
    ) -> None:
        """Initialize the Folders service."""
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_folders_by_factory(self, factory_id: UUID) -> list[SpecSheetFolder]:
        """
        Get all folders for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of Folder models
        """
        return await self.repository.find_by_factory(factory_id)

    async def create_folder(
        self, factory_id: UUID, folder_path: str
    ) -> SpecSheetFolder:
        """
        Create a new folder (and any parent folders that don't exist).

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path (e.g., "Folder1/Folder2")

        Returns:
            Created Folder
        """
        return await self.repository.create_folder(factory_id, folder_path)

    async def create_subfolder(
        self, factory_id: UUID, parent_path: str, folder_name: str
    ) -> SpecSheetFolder:
        """
        Create a new subfolder under a parent folder.

        Args:
            factory_id: UUID of the factory
            parent_path: The parent folder path (empty string for root)
            folder_name: Name of the new folder

        Returns:
            Created Folder
        """
        if parent_path:
            full_path = f"{parent_path}/{folder_name}"
        else:
            full_path = folder_name

        return await self.repository.create_folder(factory_id, full_path)

    async def rename_folder(
        self, factory_id: UUID, folder_path: str, new_name: str
    ) -> tuple[SpecSheetFolder, int]:
        """
        Rename a folder and update all spec sheets in it.

        Args:
            factory_id: UUID of the factory
            folder_path: Current folder path
            new_name: New name for the folder

        Returns:
            Tuple of (updated Folder, number of spec sheets updated)
        """
        return await self.repository.rename_folder(factory_id, folder_path, new_name)

    async def delete_folder(self, factory_id: UUID, folder_path: str) -> bool:
        """
        Delete a folder only if it has no spec sheets.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If folder has spec sheets and cannot be deleted
        """
        return await self.repository.delete_folder(factory_id, folder_path)

    async def ensure_folder_exists(
        self, factory_id: UUID, folder_path: str
    ) -> SpecSheetFolder:
        """
        Ensure a folder exists, creating it if necessary.

        Args:
            factory_id: UUID of the factory
            folder_path: The folder path

        Returns:
            The existing or created Folder
        """
        return await self.repository.ensure_folder_exists(factory_id, folder_path)
