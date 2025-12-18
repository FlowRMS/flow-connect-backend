from typing import Any

from sqlalchemy import text
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper


class AIRepository:
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__()
        self.context = context_wrapper.get()
        self.session = session

    async def get_pending_documents_landing(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Row[Any]]:
        stmt = text("""
            SELECT
                c.id as cluster_id,
                c.cluster_name,
                p.id as pending_document_id,
                p.file_id as document_id,
                p.document_type,
                p.entity_type,
                p.status as ai_status,
                p.created_at,
                f.status
            FROM
                ai.pending_documents p
            LEFT JOIN
                ai.document_clusters c ON c.id = p.cluster_id
            LEFT JOIN
                files.file_upload_process f ON f.pending_document_id = p.id
            ORDER BY
                p.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        result = await self.session.execute(stmt, {"limit": limit, "offset": offset})
        return list(result.fetchall())
