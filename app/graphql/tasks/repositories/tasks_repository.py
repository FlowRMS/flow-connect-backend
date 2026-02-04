from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core import Customer, Factory, Product
from commons.db.v6.crm import Quote
from commons.db.v6.crm.companies.company_model import Company
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.notes.note_model import Note
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.tasks.task_assignee_model import TaskAssignee
from commons.db.v6.crm.tasks.task_category_model import TaskCategory
from commons.db.v6.crm.tasks.task_model import Task
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User
from sqlalchemy import Select, case, func, literal, or_, select
from sqlalchemy.dialects.postgresql import JSONB, array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, lazyload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.tasks.processors import SyncTaskAssigneesProcessor
from app.graphql.tasks.strawberry.task_landing_page_response import (
    TaskLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy
from app.graphql.v2.rbac.strategies.sales_team_filter import SalesTeamFilterStrategy


class TasksRepository(BaseRepository[Task]):
    landing_model = TaskLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.TASK

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        sync_assignees_processor: SyncTaskAssigneesProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Task,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[sync_assignees_processor],
        )
        self.sync_assignees_processor = sync_assignees_processor

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        if RbacRoleEnum.SALES_MANAGER in self.auth_info.roles:
            return SalesTeamFilterStrategy(
                RbacResourceEnum.TASK,
                Task.created_by_id,
            )
        return CreatedByFilterStrategy(
            RbacResourceEnum.TASK,
            Task,
        )

    def paginated_stmt(self) -> Select[Any]:
        assignee_user_alias = aliased(User)

        linked_entities_subq = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            literal("id"),
                            case(
                                (
                                    LinkRelation.source_entity_type == EntityType.TASK,
                                    LinkRelation.target_entity_id,
                                ),
                                else_=LinkRelation.source_entity_id,
                            ),
                            literal("title"),
                            func.coalesce(
                                Job.job_name,
                                Note.title,
                                Contact.first_name + literal(" ") + Contact.last_name,
                                Company.name,
                                PreOpportunity.entity_number,
                                Quote.quote_number,
                                Factory.title,
                                Product.factory_part_number,
                                Customer.company_name,
                            ),
                            literal("entity_type"),
                            case(
                                (
                                    LinkRelation.source_entity_type == EntityType.TASK,
                                    LinkRelation.target_entity_type,
                                ),
                                else_=LinkRelation.source_entity_type,
                            ),
                        )
                    ),
                    literal("[]").cast(JSONB),
                )
            )
            .select_from(LinkRelation)
            .outerjoin(
                Job,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (Job.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.JOB)
                    & (Job.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Note,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.NOTE)
                    & (Note.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.NOTE)
                    & (Note.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Contact,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (Contact.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (Contact.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Company,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (Company.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (Company.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                PreOpportunity,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.PRE_OPPORTUNITY)
                    & (PreOpportunity.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.PRE_OPPORTUNITY)
                    & (PreOpportunity.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Quote,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.QUOTE)
                    & (Quote.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.QUOTE)
                    & (Quote.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Factory,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.FACTORY)
                    & (Factory.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.FACTORY)
                    & (Factory.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Product,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.PRODUCT)
                    & (Product.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.PRODUCT)
                    & (Product.id == LinkRelation.source_entity_id)
                ),
            )
            .outerjoin(
                Customer,
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.CUSTOMER)
                    & (Customer.id == LinkRelation.target_entity_id)
                )
                | (
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_type == EntityType.CUSTOMER)
                    & (Customer.id == LinkRelation.source_entity_id)
                ),
            )
            .where(
                or_(
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.source_entity_id == Task.id),
                    (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_id == Task.id),
                )
            )
            .correlate(Task)
            .scalar_subquery()
        )

        # Correlated scalar subquery for assignees
        assignees_subq = (
            select(
                func.coalesce(
                    func.jsonb_agg(
                        func.jsonb_build_object(
                            literal("id"),
                            assignee_user_alias.id,
                            literal("name"),
                            assignee_user_alias.full_name,
                        )
                    ),
                    literal("[]").cast(JSONB),
                )
            )
            .select_from(TaskAssignee)
            .join(assignee_user_alias, assignee_user_alias.id == TaskAssignee.user_id)
            .where(TaskAssignee.task_id == Task.id)
            .correlate(Task)
            .scalar_subquery()
        )

        return (
            select(
                Task.id,
                Task.created_at,
                User.full_name.label("created_by"),
                Task.title,
                Task.status,
                TaskCategory.name.label("category"),
                Task.priority,
                Task.description,
                assignees_subq.label("assignees"),
                Task.due_date,
                Task.reminder_date,
                Task.tags,
                linked_entities_subq.label("linked_entities"),
                array([Task.created_by_id]).label("user_ids"),
            )
            .select_from(Task)
            .options(lazyload("*"))
            .join(User, User.id == Task.created_by_id)
            .outerjoin(TaskCategory, Task.category_id == TaskCategory.id)
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
        stmt = (
            select(Task)
            .options(
                joinedload(Task.created_by),
                joinedload(Task.category),
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            )
            .where(Task.title.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[Task]:
        stmt = (
            select(Task)
            .options(
                joinedload(Task.created_by),
                joinedload(Task.category),
                selectinload(Task.assignees).joinedload(TaskAssignee.user),
                lazyload("*"),
            )
            .join(
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
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
