from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.files import Folder
from commons.db.v6.user import User
from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.files.strawberry.folder_landing_page_response import (
    FolderLandingPageResponse,
)


class FolderRepository(BaseRepository[Folder]):
    landing_model = FolderLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Folder)

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Folder.id,
                Folder.created_at,
                User.full_name.label("created_by"),
                Folder.name,
                Folder.description,
                Folder.parent_id,
                Folder.archived,
                array([Folder.created_by_id]).label("user_ids"),
            )
            .select_from(Folder)
            .options(lazyload("*"))
            .join(User, User.id == Folder.created_by_id)
            .where(Folder.archived.is_(False))
        )

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[Folder]:
        stmt = (
            select(Folder)
            .where(
                or_(
                    Folder.name.ilike(f"%{search_term}%"),
                    Folder.description.ilike(f"%{search_term}%"),
                )
            )
            .where(Folder.archived.is_(False))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_parent(self, parent_id: UUID | None) -> list[Folder]:
        if parent_id is None:
            stmt = (
                select(Folder)
                .where(Folder.parent_id.is_(None))
                .where(Folder.archived.is_(False))
            )
        else:
            stmt = (
                select(Folder)
                .where(Folder.parent_id == parent_id)
                .where(Folder.archived.is_(False))
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_relations(self, folder_id: UUID) -> Folder | None:
        stmt = (
            select(Folder)
            .where(Folder.id == folder_id)
            .options(
                joinedload(Folder.created_by),
                joinedload(Folder.parent),
                joinedload(Folder.children),
                joinedload(Folder.files),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def count_folders(self) -> int:
        stmt = (
            select(func.count()).select_from(Folder).where(Folder.archived.is_(False))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def archive(self, folder_id: UUID) -> bool:
        folder = await self.get_by_id(folder_id)
        if not folder:
            return False
        folder.archived = True
        await self.session.flush()
        return True

    async def get_root_folders(self) -> list[Folder]:
        return await self.find_by_parent(None)
