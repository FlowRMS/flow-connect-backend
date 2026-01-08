from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.files import Folder
from sqlalchemy.orm import joinedload, lazyload

from app.graphql.v2.files.repositories.folder_repository import FolderRepository


class FolderService:
    def __init__(
        self,
        repository: FolderRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, folder_id: UUID) -> Folder | None:
        return await self.repository.get_by_id(
            folder_id,
            options=[
                joinedload(Folder.created_by),
                lazyload("*"),
            ],
        )

    async def get_with_relations(self, folder_id: UUID) -> Folder | None:
        return await self.repository.get_with_relations(folder_id)

    async def search_folders(self, search_term: str, limit: int = 20) -> list[Folder]:
        return await self.repository.search_by_name(search_term, limit)

    async def find_by_parent(self, parent_id: UUID | None) -> list[Folder]:
        return await self.repository.find_by_parent(parent_id)

    async def get_root_folders(self) -> list[Folder]:
        return await self.repository.get_root_folders()

    async def create_folder(
        self,
        name: str,
        description: str | None = None,
        parent_id: UUID | None = None,
    ) -> Folder:
        new_folder = Folder(
            name=name,
            description=description,
            parent_id=parent_id,
            archived=False,
        )
        folder = await self.repository.create(new_folder)
        result = await self.get_by_id(folder.id)
        if not result:
            raise ValueError(f"Failed to retrieve created folder with id {folder.id}")
        return result

    async def update_folder(
        self,
        folder_id: UUID,
        name: str | None = None,
        description: str | None = None,
        parent_id: UUID | None = None,
    ) -> Folder:
        folder = await self.repository.get_by_id(folder_id)
        if not folder:
            raise ValueError(f"Folder with id {folder_id} not found")

        if name is not None:
            folder.name = name
        if description is not None:
            folder.description = description
        if parent_id is not None:
            folder.parent_id = parent_id

        updated = await self.repository.update(folder)
        result = await self.get_by_id(updated.id)
        if not result:
            raise ValueError(f"Failed to retrieve updated folder with id {updated.id}")
        return result

    async def archive_folder(self, folder_id: UUID) -> bool:
        return await self.repository.archive(folder_id)

    async def delete_folder(self, folder_id: UUID) -> bool:
        return await self.repository.delete(folder_id)
