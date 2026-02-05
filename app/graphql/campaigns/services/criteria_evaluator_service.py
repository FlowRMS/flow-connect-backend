from typing import Any

from commons.db.v6.crm.companies.company_model import Company
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.graphql.campaigns.services.criteria_operators import apply_operator
from app.graphql.campaigns.strawberry.campaign_criteria_input import (
    CampaignCriteriaInput,
)
from app.graphql.campaigns.strawberry.criteria_condition_input import (
    CriteriaConditionInput,
)
from app.graphql.campaigns.strawberry.criteria_enums import (
    CriteriaOperator,
    LogicalOperator,
)
from app.graphql.campaigns.strawberry.criteria_group_input import CriteriaGroupInput


class CriteriaEvaluatorService:
    ENTITY_MODEL_MAP: dict[EntityType, type] = {
        EntityType.CONTACT: Contact,
        EntityType.COMPANY: Company,
        EntityType.JOB: Job,
        EntityType.TASK: Task,
    }

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def evaluate_criteria(
        self,
        criteria: CampaignCriteriaInput,
        limit: int | None = None,
    ) -> list[Contact]:
        stmt = self._build_criteria_query(criteria)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_matching_contacts(self, criteria: CampaignCriteriaInput) -> int:
        stmt = self._build_criteria_query(criteria)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(count_stmt)
        return result.scalar_one()

    async def get_sample_contacts(
        self,
        criteria: CampaignCriteriaInput,
        limit: int = 10,
    ) -> list[Contact]:
        return await self.evaluate_criteria(criteria, limit=limit)

    def _build_criteria_query(
        self,
        criteria: CampaignCriteriaInput,
    ) -> Select[tuple[Contact]]:
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
        conditions = []

        for condition in group.conditions:
            sql_condition = self._build_single_condition(condition)
            # Skip None conditions (e.g., empty values for arrays)
            if sql_condition is not None:
                conditions.append(sql_condition)

        # If no valid conditions, return None to skip this group
        if not conditions:
            return None

        if group.logical_operator == LogicalOperator.AND:
            return and_(*conditions)
        return or_(*conditions)

    def _build_single_condition(self, condition: CriteriaConditionInput) -> Any:
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
        column = getattr(Contact, field, None)
        if column is None:
            return None
        return apply_operator(column, operator, value)

    def _build_linked_entity_condition(
        self,
        entity_type: EntityType,
        field: str,
        operator: CriteriaOperator,
        value: Any,
    ) -> Any:
        model = self.ENTITY_MODEL_MAP.get(entity_type)
        if model is None:
            return None

        column = getattr(model, field, None)
        if column is None:
            return None

        entity_condition = apply_operator(column, operator, value)

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
