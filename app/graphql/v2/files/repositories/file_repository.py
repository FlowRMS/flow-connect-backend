from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.files import File
from commons.db.v6.user import User
from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.files.strawberry.file_landing_page_response import (
    FileLandingPageResponse,
)


class FileRepository(BaseRepository[File]):
    landing_model = FileLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, File)

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                File.id,
                File.created_at,
                User.full_name.label("created_by"),
                File.file_name,
                File.file_path,
                File.file_size,
                File.file_type,
                File.file_sha,
                File.archived,
                File.folder_id,
                array([File.created_by_id]).label("user_ids"),
            )
            .select_from(File)
            .options(lazyload("*"))
            .join(User, User.id == File.created_by_id)
            .where(File.archived == False)  # noqa: E712
        )

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[File]:
        stmt = (
            select(File)
            .where(
                or_(
                    File.file_name.ilike(f"%{search_term}%"),
                    File.file_path.ilike(f"%{search_term}%"),
                )
            )
            .where(File.archived == False)  # noqa: E712
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_folder(self, folder_id: UUID) -> list[File]:
        stmt = (
            select(File)
            .where(File.folder_id == folder_id)
            .where(File.archived == False)  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_sha(self, file_sha: str) -> File | None:
        stmt = select(File).where(File.file_sha == file_sha)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_files(self) -> int:
        stmt = (
            select(func.count()).select_from(File).where(File.archived == False)  # noqa: E712
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def archive(self, file_id: UUID) -> bool:
        file = await self.get_by_id(file_id)
        if not file:
            return False
        file.archived = True
        await self.session.flush()
        return True
