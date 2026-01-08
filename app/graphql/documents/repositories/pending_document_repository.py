from typing import Any

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.ai.documents.document_cluster import DocumentCluster
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.files import File
from commons.db.v6.user import User
from sqlalchemy import Select, case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.documents.strawberry.pending_document_landing_page_response import (
    PendingDocumentLandingPageResponse,
)


class PendingDocumentRepository(BaseRepository[PendingDocument]):
    landing_model = PendingDocumentLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, PendingDocument)

    def paginated_stmt(self) -> Select[Any]:
        two_minutes_ago = func.now() - text("INTERVAL '2 minute'")
        is_new_expr = case(
            (PendingDocument.created_at >= two_minutes_ago, True),
            else_=False,
        )

        return (
            select(
                PendingDocument.id,
                PendingDocument.created_at,
                func.concat(User.first_name, " ", User.last_name).label("created_by"),
                User.id.label("created_by_id"),
                PendingDocument.cluster_id,
                DocumentCluster.cluster_name.label("cluster_name"),
                PendingDocument.file_id,
                File.file_name.label("file_name"),
                PendingDocument.document_type,
                PendingDocument.entity_type,
                PendingDocument.workflow_status,
                PendingDocument.status,
                is_new_expr.label("is_new"),
            )
            .select_from(PendingDocument)
            .options(lazyload("*"))
            .join(File, File.id == PendingDocument.file_id)
            .join(User, User.id == File.created_by_id)
            .outerjoin(
                DocumentCluster, DocumentCluster.id == PendingDocument.cluster_id
            )
            .where(PendingDocument.is_archived.is_(False))
        )
