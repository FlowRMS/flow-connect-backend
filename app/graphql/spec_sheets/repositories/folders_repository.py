"""Repository for spec sheet folders - facade for queries and mutations."""

from uuid import UUID

from commons.db.v6.crm.spec_sheets import SpecSheetFolder
from commons.db.v6.files import Folder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper

from .folder_mutations_repository import FolderMutationsRepository
from .folder_queries_repository import FolderQueriesRepository


class FoldersRepository:
    """
    Repository for spec sheet folders.

    Facade that delegates to FolderQueriesRepository and FolderMutationsRepository.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """Initialize the repository."""
        self.session = session
        self.context_wrapper = context_wrapper
        self._queries = FolderQueriesRepository(context_wrapper, session)
        self._mutations = FolderMutationsRepository(session, self._queries)

    # Query methods (delegated to FolderQueriesRepository)

    async def find_by_factory(self, factory_id: UUID) -> list[Folder]:
        """Find all pyfiles.folders for a given factory."""
        return await self._queries.find_by_factory(factory_id)

    async def find_by_factory_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[Folder, int]]:
        """Find all folders for a factory with spec sheet counts."""
        return await self._queries.find_by_factory_with_counts(factory_id)

    async def get_folders_with_hierarchy(
        self, factory_id: UUID
    ) -> list[tuple[Folder, int]]:
        """Get all folders for a factory with recursive spec sheet counts."""
        return await self._queries.get_folders_with_hierarchy(factory_id)

    async def find_by_id(self, folder_id: UUID) -> Folder | None:
        """Find a pyfiles.folder by ID."""
        return await self._queries.find_by_id(folder_id)

    async def find_by_id_with_relations(self, folder_id: UUID) -> Folder | None:
        """Find a folder by ID with parent and children loaded."""
        return await self._queries.find_by_id_with_relations(folder_id)

    async def get_mapping(
        self, factory_id: UUID, folder_id: UUID
    ) -> SpecSheetFolder | None:
        """Get the spec_sheet_folders mapping record."""
        return await self._queries.get_mapping(factory_id, folder_id)

    async def get_spec_sheet_count(self, factory_id: UUID, folder_id: UUID) -> int:
        """Get the count of spec sheets in a folder."""
        return await self._queries.get_spec_sheet_count(factory_id, folder_id)

    async def get_root_folders(self, factory_id: UUID) -> list[Folder]:
        """Get root folders for a factory."""
        return await self._queries.get_root_folders(factory_id)

    async def get_children(self, factory_id: UUID, parent_id: UUID) -> list[Folder]:
        """Get child folders of a parent folder."""
        return await self._queries.get_children(factory_id, parent_id)

    # Mutation methods (delegated to FolderMutationsRepository)

    async def create_folder(
        self,
        factory_id: UUID,
        name: str,
        created_by_id: UUID,
        parent_id: UUID | None = None,
    ) -> Folder:
        """Create a new folder and map it to the factory."""
        return await self._mutations.create_folder(
            factory_id, name, created_by_id, parent_id
        )

    async def rename_folder(
        self, factory_id: UUID, folder_id: UUID, new_name: str
    ) -> Folder:
        """Rename a folder."""
        return await self._mutations.rename_folder(factory_id, folder_id, new_name)

    async def delete_folder(self, factory_id: UUID, folder_id: UUID) -> bool:
        """Delete a folder only if empty."""
        return await self._mutations.delete_folder(factory_id, folder_id)

    async def move_folder(
        self,
        factory_id: UUID,
        folder_id: UUID,
        new_parent_id: UUID | None,
    ) -> Folder:
        """Move a folder to a new parent."""
        return await self._mutations.move_folder(factory_id, folder_id, new_parent_id)

    async def ensure_folder_exists(
        self,
        factory_id: UUID,
        folder_id: UUID,
    ) -> Folder | None:
        """Ensure a folder mapping exists for the factory."""
        return await self._mutations.ensure_folder_exists(factory_id, folder_id)
