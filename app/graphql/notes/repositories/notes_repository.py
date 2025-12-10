"""Repository for Note entity."""

from typing import Any
from uuid import UUID

from commons.db.models import (
    Check,
    Customer,
    Factory,
    Invoice,
    Order,
    Product,
    Quote,
    User,
)
from sqlalchemy import Select, case, func, literal, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.companies.models.company_model import Company
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
from app.graphql.notes.models.note_model import Note
from app.graphql.notes.strawberry.note_landing_page_response import (
    NoteLandingPageResponse,
)
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.tasks.models.task_model import Task


class NotesRepository(BaseRepository[Note]):
    """Repository for Notes entity."""

    landing_model = NoteLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Note)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for notes landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        # Build a CTE that flattens link relations with entity info
        # This ensures proper handling of the bidirectional link structure
        note_id_col = case(
            (
                LinkRelation.source_entity_type == EntityType.NOTE,
                LinkRelation.source_entity_id,
            ),
            else_=LinkRelation.target_entity_id,
        ).label("note_id")

        entity_type_col = case(
            (
                LinkRelation.source_entity_type == EntityType.NOTE,
                LinkRelation.target_entity_type,
            ),
            else_=LinkRelation.source_entity_type,
        ).label("entity_type")

        entity_id_col = case(
            (
                LinkRelation.source_entity_type == EntityType.NOTE,
                LinkRelation.target_entity_id,
            ),
            else_=LinkRelation.source_entity_id,
        ).label("entity_id")

        # CTE to extract note links with entity type and id
        links_cte = (
            select(note_id_col, entity_type_col, entity_id_col)
            .select_from(LinkRelation)
            .where(
                or_(
                    LinkRelation.source_entity_type == EntityType.NOTE,
                    LinkRelation.target_entity_type == EntityType.NOTE,
                )
            )
            .cte("note_links")
        )

        # Build CASE expression to get title based on entity type
        linked_title = case(
            (links_cte.c.entity_type == EntityType.JOB, Job.job_name),
            (links_cte.c.entity_type == EntityType.TASK, Task.title),
            (
                links_cte.c.entity_type == EntityType.CONTACT,
                Contact.first_name + literal(" ") + Contact.last_name,
            ),
            (links_cte.c.entity_type == EntityType.COMPANY, Company.name),
            (
                links_cte.c.entity_type == EntityType.PRE_OPPORTUNITY,
                PreOpportunity.entity_number,
            ),
            (links_cte.c.entity_type == EntityType.QUOTE, Quote.quote_number),
            (links_cte.c.entity_type == EntityType.ORDER, Order.order_number),
            (links_cte.c.entity_type == EntityType.INVOICE, Invoice.invoice_number),
            (links_cte.c.entity_type == EntityType.CHECK, Check.check_number),
            (links_cte.c.entity_type == EntityType.FACTORY, Factory.title),
            (
                links_cte.c.entity_type == EntityType.PRODUCT,
                Product.factory_part_number,
            ),
            (links_cte.c.entity_type == EntityType.CUSTOMER, Customer.company_name),
            else_=literal(None),
        )

        # Build JSON object for linked entity with id, title, and entity_type
        linked_entity_json = func.jsonb_build_object(
            literal("id"),
            links_cte.c.entity_id,
            literal("title"),
            linked_title,
            literal("entity_type"),
            links_cte.c.entity_type,
        )

        # Subquery to aggregate linked entities for each note
        linked_entities_subq = (
            select(
                links_cte.c.note_id,
                func.coalesce(
                    func.jsonb_agg(linked_entity_json).filter(linked_title.isnot(None)),
                    literal("[]").cast(JSONB),
                ).label("linked_entities"),
            )
            .select_from(links_cte)
            .outerjoin(
                Job,
                (links_cte.c.entity_type == EntityType.JOB)
                & (links_cte.c.entity_id == Job.id),
            )
            .outerjoin(
                Task,
                (links_cte.c.entity_type == EntityType.TASK)
                & (links_cte.c.entity_id == Task.id),
            )
            .outerjoin(
                Contact,
                (links_cte.c.entity_type == EntityType.CONTACT)
                & (links_cte.c.entity_id == Contact.id),
            )
            .outerjoin(
                Company,
                (links_cte.c.entity_type == EntityType.COMPANY)
                & (links_cte.c.entity_id == Company.id),
            )
            .outerjoin(
                PreOpportunity,
                (links_cte.c.entity_type == EntityType.PRE_OPPORTUNITY)
                & (links_cte.c.entity_id == PreOpportunity.id),
            )
            .outerjoin(
                Quote,
                (links_cte.c.entity_type == EntityType.QUOTE)
                & (links_cte.c.entity_id == Quote.id),
            )
            .outerjoin(
                Order,
                (links_cte.c.entity_type == EntityType.ORDER)
                & (links_cte.c.entity_id == Order.id),
            )
            .outerjoin(
                Invoice,
                (links_cte.c.entity_type == EntityType.INVOICE)
                & (links_cte.c.entity_id == Invoice.id),
            )
            .outerjoin(
                Check,
                (links_cte.c.entity_type == EntityType.CHECK)
                & (links_cte.c.entity_id == Check.id),
            )
            .outerjoin(
                Factory,
                (links_cte.c.entity_type == EntityType.FACTORY)
                & (links_cte.c.entity_id == Factory.id),
            )
            .outerjoin(
                Product,
                (links_cte.c.entity_type == EntityType.PRODUCT)
                & (links_cte.c.entity_id == Product.id),
            )
            .outerjoin(
                Customer,
                (links_cte.c.entity_type == EntityType.CUSTOMER)
                & (links_cte.c.entity_id == Customer.id),
            )
            .group_by(links_cte.c.note_id)
            .subquery()
        )

        return (
            select(
                Note.id,
                Note.created_at,
                User.full_name.label("created_by"),
                Note.title,
                Note.content,
                Note.tags,
                Note.mentions,
                func.coalesce(
                    linked_entities_subq.c.linked_entities, literal("[]").cast(JSONB)
                ).label("linked_entities"),
            )
            .select_from(Note)
            .options(lazyload("*"))
            .join(User, User.id == Note.created_by_id)
            .outerjoin(linked_entities_subq, linked_entities_subq.c.note_id == Note.id)
        )

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Note]:
        """Find all notes linked to a specific entity via link relations."""
        # First, get all link relations where:
        # - Source is NOTE and target is the given entity, OR
        # - Target is NOTE and source is the given entity
        links_stmt = select(LinkRelation).where(
            (
                (LinkRelation.source_entity_type == EntityType.NOTE)
                & (LinkRelation.target_entity_type == entity_type)
                & (LinkRelation.target_entity_id == entity_id)
            )
            | (
                (LinkRelation.target_entity_type == EntityType.NOTE)
                & (LinkRelation.source_entity_type == entity_type)
                & (LinkRelation.source_entity_id == entity_id)
            )
        )
        links_result = await self.session.execute(links_stmt)
        links = list(links_result.scalars().all())

        if not links:
            return []

        # Extract note IDs from the links
        note_ids: list[UUID] = []
        for link in links:
            if link.source_entity_type == EntityType.NOTE:
                note_ids.append(link.source_entity_id)
            elif link.target_entity_type == EntityType.NOTE:
                note_ids.append(link.target_entity_id)

        # Query notes with those IDs
        notes_stmt = select(Note).where(Note.id.in_(note_ids))
        notes_result = await self.session.execute(notes_stmt)
        return list(notes_result.scalars().all())

    async def search_by_title_or_content(
        self, search_term: str, limit: int = 20
    ) -> list[Note]:
        """
        Search notes by title or content using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against note title or content
            limit: Maximum number of notes to return (default: 20)

        Returns:
            List of Note objects matching the search criteria
        """
        stmt = (
            select(Note)
            .where(
                or_(
                    Note.title.ilike(f"%{search_term}%"),
                    Note.content.ilike(f"%{search_term}%"),
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
