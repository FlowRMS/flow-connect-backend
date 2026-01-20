"""Repository for spec sheet folder query operations."""

from uuid import UUID

from commons.db.v6.crm.spec_sheets import SpecSheet, SpecSheetFolder
from commons.db.v6.files import File, Folder
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FolderQueriesRepository(BaseRepository[SpecSheetFolder]):
    """Repository for spec sheet folder query operations."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """Initialize the repository."""
        super().__init__(session, context_wrapper, SpecSheetFolder)

    async def find_by_factory(self, factory_id: UUID) -> list[Folder]:
        """
        Find all pyfiles.folders for a given factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of pyfiles.Folder models
        """
        stmt = (
            select(Folder)
            .join(
                SpecSheetFolder,
                SpecSheetFolder.pyfiles_folder_id == Folder.id,
            )
            .where(SpecSheetFolder.factory_id == factory_id)
            .where(Folder.archived.is_(False))
            .order_by(Folder.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_factory_with_counts(
        self, factory_id: UUID
    ) -> list[tuple[Folder, int]]:
        """
        Find all folders for a factory with spec sheet counts.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (Folder, spec_sheet_count)
        """
        count_subquery = (
            select(
                File.folder_id,
                func.count().label("spec_count"),
            )
            .join(SpecSheet, SpecSheet.file_id == File.id)
            .where(SpecSheet.factory_id == factory_id)
            .where(File.folder_id.isnot(None))
            .group_by(File.folder_id)
            .subquery()
        )

        stmt = (
            select(
                Folder,
                func.coalesce(count_subquery.c.spec_count, 0).label("spec_count"),
            )
            .join(
                SpecSheetFolder,
                SpecSheetFolder.pyfiles_folder_id == Folder.id,
            )
            .outerjoin(
                count_subquery,
                Folder.id == count_subquery.c.folder_id,
            )
            .where(SpecSheetFolder.factory_id == factory_id)
            .where(Folder.archived.is_(False))
            .order_by(Folder.name)
        )

        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_folders_with_hierarchy(
        self, factory_id: UUID
    ) -> list[tuple[Folder, int]]:
        """
        Get all folders for a factory with recursive spec sheet counts.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of tuples (Folder, recursive_spec_sheet_count)
        """
        folders = await self.find_by_factory(factory_id)

        count_stmt = (
            select(
                File.folder_id,
                func.count().label("spec_count"),
            )
            .join(SpecSheet, SpecSheet.file_id == File.id)
            .where(SpecSheet.factory_id == factory_id)
            .where(File.folder_id.isnot(None))
            .group_by(File.folder_id)
        )
        count_result = await self.session.execute(count_stmt)
        direct_counts: dict[UUID, int] = {
            row.folder_id: row.spec_count for row in count_result.all()
        }

        folder_map: dict[UUID, Folder] = {f.id: f for f in folders}
        children_map: dict[UUID | None, list[UUID]] = {}
        for folder in folders:
            parent_id = folder.parent_id
            if parent_id not in children_map:
                children_map[parent_id] = []
            children_map[parent_id].append(folder.id)

        def get_recursive_count(folder_id: UUID) -> int:
            count = direct_counts.get(folder_id, 0)
            for child_id in children_map.get(folder_id, []):
                count += get_recursive_count(child_id)
            return count

        result: list[tuple[Folder, int]] = []
        for folder in folders:
            recursive_count = get_recursive_count(folder.id)
            result.append((folder, recursive_count))

        return result

    async def find_by_id(self, folder_id: UUID) -> Folder | None:
        """
        Find a pyfiles.folder by ID.

        Args:
            folder_id: UUID of the folder

        Returns:
            Folder if found, None otherwise
        """
        stmt = (
            select(Folder)
            .where(Folder.id == folder_id)
            .where(Folder.archived.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_with_relations(self, folder_id: UUID) -> Folder | None:
        """
        Find a folder by ID with parent and children loaded.

        Args:
            folder_id: UUID of the folder

        Returns:
            Folder with relations if found, None otherwise
        """
        stmt = (
            select(Folder)
            .where(Folder.id == folder_id)
            .where(Folder.archived.is_(False))
            .options(
                joinedload(Folder.parent),
                joinedload(Folder.children),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_mapping(
        self, factory_id: UUID, folder_id: UUID
    ) -> SpecSheetFolder | None:
        """
        Get the spec_sheet_folders mapping record.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the pyfiles.folder

        Returns:
            SpecSheetFolder mapping if found, None otherwise
        """
        stmt = select(SpecSheetFolder).where(
            and_(
                SpecSheetFolder.factory_id == factory_id,
                SpecSheetFolder.pyfiles_folder_id == folder_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_spec_sheet_count(self, factory_id: UUID, folder_id: UUID) -> int:
        """
        Get the count of spec sheets in a folder (not including subfolders).

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder

        Returns:
            Number of spec sheets in the folder
        """
        stmt = (
            select(func.count())
            .select_from(SpecSheet)
            .join(File, File.id == SpecSheet.file_id)
            .where(SpecSheet.factory_id == factory_id)
            .where(File.folder_id == folder_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_root_folders(self, factory_id: UUID) -> list[Folder]:
        """
        Get root folders for a factory (folders with no parent).

        Args:
            factory_id: UUID of the factory

        Returns:
            List of root Folder models
        """
        stmt = (
            select(Folder)
            .join(
                SpecSheetFolder,
                SpecSheetFolder.pyfiles_folder_id == Folder.id,
            )
            .where(SpecSheetFolder.factory_id == factory_id)
            .where(Folder.parent_id.is_(None))
            .where(Folder.archived.is_(False))
            .order_by(Folder.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, factory_id: UUID, parent_id: UUID) -> list[Folder]:
        """
        Get child folders of a parent folder.

        Args:
            factory_id: UUID of the factory
            parent_id: UUID of the parent folder

        Returns:
            List of child Folder models
        """
        stmt = (
            select(Folder)
            .join(
                SpecSheetFolder,
                SpecSheetFolder.pyfiles_folder_id == Folder.id,
            )
            .where(SpecSheetFolder.factory_id == factory_id)
            .where(Folder.parent_id == parent_id)
            .where(Folder.archived.is_(False))
            .order_by(Folder.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
