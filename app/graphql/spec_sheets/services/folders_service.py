"""Service for spec sheet folder management using pyfiles.folders."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.files import Folder

from app.graphql.spec_sheets.repositories.folders_repository import FoldersRepository


class FoldersService:
    """Service for spec sheet folder business logic using pyfiles.folders."""

    def __init__(
        self,
        repository: FoldersRepository,
        auth_info: AuthInfo,
    ) -> None:
        """Initialize the Folders service."""
        self.repository = repository
        self.auth_info = auth_info

    async def get_folders_by_factory(self, factory_id: UUID) -> list[Folder]:
        """
        Get all folders for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of pyfiles.Folder models
        """
        return await self.repository.find_by_factory(factory_id)

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
        return await self.repository.get_folders_with_hierarchy(factory_id)

    async def get_folder(self, folder_id: UUID) -> Folder | None:
        """
        Get a folder by ID.

        Args:
            folder_id: UUID of the folder

        Returns:
            Folder if found, None otherwise
        """
        return await self.repository.find_by_id(folder_id)

    async def get_folder_with_relations(self, folder_id: UUID) -> Folder | None:
        """
        Get a folder with parent and children loaded.

        Args:
            folder_id: UUID of the folder

        Returns:
            Folder with relations if found, None otherwise
        """
        return await self.repository.find_by_id_with_relations(folder_id)

    async def create_folder(
        self,
        factory_id: UUID,
        name: str,
        parent_folder_id: UUID | None = None,
    ) -> Folder:
        """
        Create a new folder for a factory.

        Args:
            factory_id: UUID of the factory
            name: Name of the folder
            parent_folder_id: Optional parent folder ID

        Returns:
            Created Folder
        """
        return await self.repository.create_folder(
            factory_id=factory_id,
            name=name,
            created_by_id=self.auth_info.flow_user_id,
            parent_id=parent_folder_id,
        )

    async def create_subfolder(
        self,
        factory_id: UUID,
        parent_folder_id: UUID,
        folder_name: str,
    ) -> Folder:
        """
        Create a new subfolder under a parent folder.

        Args:
            factory_id: UUID of the factory
            parent_folder_id: UUID of the parent folder
            folder_name: Name of the new folder

        Returns:
            Created Folder
        """
        return await self.repository.create_folder(
            factory_id=factory_id,
            name=folder_name,
            created_by_id=self.auth_info.flow_user_id,
            parent_id=parent_folder_id,
        )

    async def rename_folder(
        self,
        factory_id: UUID,
        folder_id: UUID,
        new_name: str,
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
        return await self.repository.rename_folder(
            factory_id=factory_id,
            folder_id=folder_id,
            new_name=new_name,
        )

    async def delete_folder(self, factory_id: UUID, folder_id: UUID) -> bool:
        """
        Delete a folder only if it has no spec sheets.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder to delete

        Returns:
            True if deleted

        Raises:
            ValueError: If folder has spec sheets and cannot be deleted
        """
        return await self.repository.delete_folder(factory_id, folder_id)

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
        return await self.repository.move_folder(
            factory_id=factory_id,
            folder_id=folder_id,
            new_parent_id=new_parent_id,
        )

    async def get_root_folders(self, factory_id: UUID) -> list[Folder]:
        """
        Get root folders (no parent) for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of root Folder models
        """
        return await self.repository.get_root_folders(factory_id)

    async def get_children(self, factory_id: UUID, parent_id: UUID) -> list[Folder]:
        """
        Get child folders of a parent folder.

        Args:
            factory_id: UUID of the factory
            parent_id: UUID of the parent folder

        Returns:
            List of child Folder models
        """
        return await self.repository.get_children(factory_id, parent_id)

    async def get_spec_sheet_count(self, factory_id: UUID, folder_id: UUID) -> int:
        """
        Get the count of spec sheets in a folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder

        Returns:
            Number of spec sheets in the folder
        """
        return await self.repository.get_spec_sheet_count(factory_id, folder_id)
