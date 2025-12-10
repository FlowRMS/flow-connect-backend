"""Service for evaluating campaign criteria and returning matching contacts."""

from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.graphql.campaigns.strawberry.criteria_input import (
    CampaignCriteriaInput,
    CriteriaConditionInput,
    CriteriaGroupInput,
    CriteriaOperator,
    LogicalOperator,
)
from app.graphql.companies.models.company_model import Company
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
from app.graphql.tasks.models.task_model import Task


class CriteriaEvaluatorService:
    """Service for evaluating criteria and finding matching contacts."""

    ENTITY_MODEL_MAP: dict[EntityType, type] = {
        EntityType.CONTACT: Contact,
        EntityType.COMPANY: Company,
        EntityType.JOB: Job,
        EntityType.TASK: Task,
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def evaluate_criteria(
        self,
        criteria: CampaignCriteriaInput,
        limit: int | None = None,
    ) -> list[Contact]:
        """Evaluate criteria and return matching contacts."""
        stmt = self._build_criteria_query(criteria)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_matching_contacts(self, criteria: CampaignCriteriaInput) -> int:
        """Count contacts matching the criteria without loading them."""
        stmt = self._build_criteria_query(criteria)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()

    async def get_sample_contacts(
        self,
        criteria: CampaignCriteriaInput,
        limit: int = 10,
    ) -> list[Contact]:
        """Get sample contacts for preview with full contact information."""
        return await self.evaluate_criteria(criteria, limit=limit)

    def _build_criteria_query(
        self,
        criteria: CampaignCriteriaInput,
    ) -> Select[tuple[Contact]]:
        """Build SQLAlchemy query from criteria definition."""
        base_query = select(Contact).distinct()

        group_conditions = []
        for group in criteria.groups:
            group_condition = self._build_group_condition(group)
            if group_condition is not None:
                group_conditions.append(group_condition)

        if group_conditions:
            if criteria.group_operator == LogicalOperator.AND:
                base_query = base_query.where(and_(*group_conditions))
            else:
                base_query = base_query.where(or_(*group_conditions))

        return base_query

    def _build_group_condition(self, group: CriteriaGroupInput) -> Any:
        """Build condition for a single criteria group."""
        conditions = []

        for condition in group.conditions:
            sql_condition = self._build_single_condition(condition)
            if sql_condition is not None:
                conditions.append(sql_condition)

        if not conditions:
            return None

        if group.logical_operator == LogicalOperator.AND:
            return and_(*conditions)
        return or_(*conditions)

    def _build_single_condition(self, condition: CriteriaConditionInput) -> Any:
        """Build SQL condition for a single criteria condition."""
        entity_type = condition.entity_type
        field = condition.field
        operator = condition.operator
        value = condition.value

        if entity_type == EntityType.CONTACT:
            return self._build_contact_condition(field, operator, value)

        return self._build_linked_entity_condition(entity_type, field, operator, value)

    def _build_contact_condition(
        self,
        field: str,
        operator: CriteriaOperator,
        value: Any,
    ) -> Any:
        """Build condition for Contact entity fields."""
        column = getattr(Contact, field, None)
        if column is None:
            return None
        return self._apply_operator(column, operator, value)

    def _build_linked_entity_condition(
        self,
        entity_type: EntityType,
        field: str,
        operator: CriteriaOperator,
        value: Any,
    ) -> Any:
        """Build condition for entities linked to Contact via LinkRelation."""
        model = self.ENTITY_MODEL_MAP.get(entity_type)
        if model is None:
            return None

        column = getattr(model, field, None)
        if column is None:
            return None

        entity_condition = self._apply_operator(column, operator, value)

        linked_contacts_subq = (
            select(Contact.id)
            .join(
                LinkRelation,
                or_(
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == entity_type)
                    & (LinkRelation.source_entity_id == Contact.id),
                    (LinkRelation.source_entity_type == entity_type)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_id == Contact.id),
                ),
            )
            .join(
                model,
                or_(
                    (LinkRelation.target_entity_id == model.id)
                    & (LinkRelation.target_entity_type == entity_type),
                    (LinkRelation.source_entity_id == model.id)
                    & (LinkRelation.source_entity_type == entity_type),
                ),
            )
            .where(entity_condition)
        )

        return Contact.id.in_(linked_contacts_subq)

    def _apply_operator(
        self,
        column: Any,
        operator: CriteriaOperator,
        value: Any,
    ) -> Any:
        """Apply operator to column comparison."""
        match operator:
            case CriteriaOperator.EQUALS:
                return column == value
            case CriteriaOperator.NOT_EQUALS:
                return column != value
            case CriteriaOperator.CONTAINS:
                return column.ilike(f"%{value}%")
            case CriteriaOperator.NOT_CONTAINS:
                return ~column.ilike(f"%{value}%")
            case CriteriaOperator.GREATER_THAN:
                return column > value
            case CriteriaOperator.LESS_THAN:
                return column < value
            case CriteriaOperator.GREATER_THAN_OR_EQUALS:
                return column >= value
            case CriteriaOperator.LESS_THAN_OR_EQUALS:
                return column <= value
            case CriteriaOperator.IS_NULL:
                return column.is_(None)
            case CriteriaOperator.IS_NOT_NULL:
                return column.isnot(None)
            case CriteriaOperator.IN:
                return column.in_(value if isinstance(value, list) else [value])
            case CriteriaOperator.NOT_IN:
                return ~column.in_(value if isinstance(value, list) else [value])
            case _:
                return column == value
