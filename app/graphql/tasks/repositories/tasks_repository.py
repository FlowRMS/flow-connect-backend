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
from sqlalchemy import ARRAY, Select, String, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.companies.models.company_model import Company
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.tasks.models.task_model import Task
from app.graphql.tasks.strawberry.task_landing_page_response import (
    TaskLandingPageResponse,
)


class TasksRepository(BaseRepository[Task]):
    """Repository for Tasks entity."""

    landing_model = TaskLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Task)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for tasks landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        # Lazy import to avoid circular dependency
        from app.graphql.notes.models.note_model import Note

        assigned_to_alias = aliased(User)

        # Build a CTE that flattens link relations with entity info
        # This ensures proper handling of the bidirectional link structure
        task_id_col = case(
            (
                LinkRelation.source_entity_type == EntityType.TASK,
                LinkRelation.source_entity_id,
            ),
            else_=LinkRelation.target_entity_id,
        ).label("task_id")

        entity_type_col = case(
            (
                LinkRelation.source_entity_type == EntityType.TASK,
                LinkRelation.target_entity_type,
            ),
            else_=LinkRelation.source_entity_type,
        ).label("entity_type")

        entity_id_col = case(
            (
                LinkRelation.source_entity_type == EntityType.TASK,
                LinkRelation.target_entity_id,
            ),
            else_=LinkRelation.source_entity_id,
        ).label("entity_id")

        # CTE to extract task links with entity type and id
        links_cte = (
            select(task_id_col, entity_type_col, entity_id_col)
            .select_from(LinkRelation)
            .where(
                or_(
                    LinkRelation.source_entity_type == EntityType.TASK,
                    LinkRelation.target_entity_type == EntityType.TASK,
                )
            )
            .cte("task_links")
        )

        # Build CASE expression to get title based on entity type
        linked_title = case(
            (links_cte.c.entity_type == EntityType.JOB, Job.job_name),
            (links_cte.c.entity_type == EntityType.NOTE, Note.title),
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

        # Subquery to aggregate linked titles for each task
        linked_titles_subq = (
            select(
                links_cte.c.task_id,
                func.coalesce(
                    func.array_agg(func.distinct(linked_title)).filter(
                        linked_title.isnot(None)
                    ),
                    literal([]).cast(ARRAY(String)),
                ).label("linked_titles"),
            )
            .select_from(links_cte)
            .outerjoin(
                Job,
                (links_cte.c.entity_type == EntityType.JOB)
                & (links_cte.c.entity_id == Job.id),
            )
            .outerjoin(
                Note,
                (links_cte.c.entity_type == EntityType.NOTE)
                & (links_cte.c.entity_id == Note.id),
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
            .group_by(links_cte.c.task_id)
            .subquery()
        )

        return (
            select(
                Task.id,
                Task.created_at,
                User.full_name.label("created_by"),
                Task.title,
                Task.status,
                Task.priority,
                Task.description,
                assigned_to_alias.full_name.label("assigned_to"),
                Task.due_date,
                Task.reminder_date,
                Task.tags,
                func.coalesce(
                    linked_titles_subq.c.linked_titles, literal([]).cast(ARRAY(String))
                ).label("linked_titles"),
            )
            .select_from(Task)
            .options(lazyload("*"))
            .join(User, User.id == Task.created_by_id)
            .outerjoin(assigned_to_alias, assigned_to_alias.id == Task.assigned_to_id)
            .outerjoin(linked_titles_subq, linked_titles_subq.c.task_id == Task.id)
        )

    async def search_by_title(self, search_term: str, limit: int = 20) -> list[Task]:
        """
        Search tasks by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against task title
            limit: Maximum number of tasks to return (default: 20)

        Returns:
            List of Task objects matching the search criteria
        """
        stmt = select(Task).where(Task.title.ilike(f"%{search_term}%")).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Task]:
        """Find all tasks linked to a specific entity via link relations."""
        stmt = select(Task).join(
            LinkRelation,
            or_(
                # Tasks as source, entity as target
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == entity_type)
                    & (LinkRelation.target_entity_id == entity_id)
                    & (LinkRelation.source_entity_id == Task.id)
                ),
                # Entity as source, Tasks as target
                (
                    (LinkRelation.source_entity_type == entity_type)
                    & (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_id == entity_id)
                    & (LinkRelation.target_entity_id == Task.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
