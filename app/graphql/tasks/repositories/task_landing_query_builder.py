from typing import Any

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
from commons.db.v6.user import User
from sqlalchemy import Select, case, func, literal, or_, select
from sqlalchemy.dialects.postgresql import JSONB, array
from sqlalchemy.orm import aliased, lazyload


class TaskLandingQueryBuilder:
    def _linked_entities_subquery(self) -> Any:
        return (
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

    def _assignees_subquery(self) -> Any:
        assignee_user_alias = aliased(User)
        return (
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

    def build(self) -> Select[Any]:
        linked_entities_subq = self._linked_entities_subquery()
        assignees_subq = self._assignees_subquery()

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
