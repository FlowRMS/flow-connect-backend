"""Repository for Invoice entity with specific database operations."""

from uuid import UUID

from commons.db.v6.commission import Invoice
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class InvoicesRepository(BaseRepository[Invoice]):
    """Repository for Invoices entity."""

    entity_type = EntityType.INVOICE

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Invoice)

    async def search_by_invoice_number(
        self, search_term: str, limit: int = 20
    ) -> list[Invoice]:
        """
        Search invoices by invoice number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against invoice number
            limit: Maximum number of invoices to return (default: 20)

        Returns:
            List of Invoice objects matching the search criteria
        """
        stmt = (
            select(Invoice)
            .options(lazyload("*"))
            .where(Invoice.invoice_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Invoice]:
        """
        Find all invoices linked to the given job ID.

        Args:
            job_id: The job ID to find invoices for

        Returns:
            List of Invoice objects linked to the given job ID
        """
        stmt = (
            select(Invoice)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.INVOICE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Invoice.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.INVOICE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Invoice.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
