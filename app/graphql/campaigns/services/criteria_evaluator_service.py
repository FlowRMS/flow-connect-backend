"""Service for evaluating campaign criteria and returning matching contacts."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from commons.db.int_enum import IntEnum as IntEnumColumn
from sqlalchemy import ARRAY, Date, String, Text, and_, func, or_, select
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
        super().__init__()
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

    def _convert_value(self, column: Any, value: Any) -> Any:
        """
        Convert a value to match the column's expected type.

        Handles:
        - IntEnum columns: converts string enum names to integer values (case-insensitive)
        - Date columns: converts ISO date strings to date objects
        - UUID columns: converts string UUIDs to UUID objects
        - Boolean columns: converts string booleans to bool
        - Lists: recursively converts each element
        """
        if value is None:
            return None

        # Handle lists by converting each element
        if isinstance(value, list):
            return [self._convert_value(column, v) for v in value]

        # Get the column type from SQLAlchemy
        try:
            column_type = column.type
        except AttributeError:
            return value

        # Handle IntEnum columns (stored as SMALLINT)
        # The IntEnum TypeDecorator uses _enumtype attribute
        if isinstance(column_type, IntEnumColumn):
            enum_class = getattr(column_type, "_enumtype", None)
            if enum_class is None:
                return value
            if isinstance(value, str):
                # Case-insensitive enum lookup
                value_upper = value.upper()
                for member in enum_class:
                    if member.name.upper() == value_upper:
                        return member
                # If not found by name, try to parse as integer
                try:
                    return enum_class(int(value))
                except (ValueError, KeyError):
                    pass
            elif isinstance(value, int):
                try:
                    return enum_class(value)
                except (ValueError, KeyError):
                    pass
            return value

        # Handle Date columns
        if isinstance(column_type, Date):
            if isinstance(value, str):
                # Empty string should return None for dates
                if not value.strip():
                    return None
                # Try ISO format first (YYYY-MM-DD)
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    pass
                # Try other common formats
                for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
            elif isinstance(value, datetime):
                return value.date()
            elif isinstance(value, date):
                return value
            return value

        # Handle UUID columns
        type_name = type(column_type).__name__
        if type_name == "UUID":
            if isinstance(value, str):
                try:
                    return UUID(value)
                except ValueError:
                    pass
            return value

        # Handle Boolean columns
        if type_name == "Boolean":
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)

        # Handle String columns - ensure string type
        if isinstance(column_type, String) and not isinstance(value, str):
            return str(value)

        return value

    def _is_string_column(self, column: Any) -> bool:
        """Check if a column is a string/text type."""
        try:
            column_type = column.type
            return isinstance(column_type, (String, Text))
        except AttributeError:
            return False

    def _is_array_column(self, column: Any) -> bool:
        """Check if a column is an ARRAY type."""
        try:
            column_type = column.type
            return isinstance(column_type, ARRAY)
        except AttributeError:
            return False

    def _apply_operator(
        self,
        column: Any,
        operator: CriteriaOperator,
        value: Any,
    ) -> Any:
        """Apply operator to column comparison with automatic type conversion."""
        # Check if column is an array type
        is_array = self._is_array_column(column)

        # Handle empty string values
        if isinstance(value, str) and not value.strip():
            # For array columns with empty value, skip the condition
            if is_array:
                return None
            # For date columns, empty string means NULL
            try:
                if isinstance(column.type, Date):
                    if operator in (CriteriaOperator.EQUALS, CriteriaOperator.IS_NULL):
                        return column.is_(None)
                    elif operator == CriteriaOperator.NOT_EQUALS:
                        return column.isnot(None)
                    else:
                        return None
            except AttributeError:
                pass

        # Convert value to match column type (except for NULL checks and string operations)
        if operator not in (
            CriteriaOperator.IS_NULL,
            CriteriaOperator.IS_NOT_NULL,
            CriteriaOperator.CONTAINS,
            CriteriaOperator.NOT_CONTAINS,
        ):
            value = self._convert_value(column, value)

        # Skip None values that resulted from conversion failures
        if value is None and operator not in (
            CriteriaOperator.IS_NULL,
            CriteriaOperator.IS_NOT_NULL,
        ):
            return None

        # Check if column is string type for case-insensitive comparisons
        is_string = self._is_string_column(column)

        match operator:
            case CriteriaOperator.EQUALS:
                # Array columns need special handling
                if is_array:
                    # For arrays, use array contains operator (@>)
                    if isinstance(value, list):
                        return column.contains(value)
                    else:
                        # Single value - check if array contains it
                        return column.any(value)
                # Use case-insensitive comparison for string columns
                if is_string and isinstance(value, str):
                    return func.lower(column) == func.lower(value)
                return column == value
            case CriteriaOperator.NOT_EQUALS:
                if is_array:
                    # For arrays, use NOT array contains operator
                    if isinstance(value, list):
                        return ~column.contains(value)
                    else:
                        return ~column.any(value)
                if is_string and isinstance(value, str):
                    return func.lower(column) != func.lower(value)
                return column != value
            case CriteriaOperator.CONTAINS:
                if is_array:
                    # For array columns, check if any element contains the value
                    return column.any(value)
                # ilike is already case-insensitive
                return column.ilike(f"%{value}%")
            case CriteriaOperator.NOT_CONTAINS:
                if is_array:
                    return ~column.any(value)
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
                converted = self._convert_value(
                    column, value if isinstance(value, list) else [value]
                )
                # Use case-insensitive IN for string columns
                if (
                    is_string
                    and converted
                    and all(isinstance(v, str) for v in converted)
                ):
                    return func.lower(column).in_([v.lower() for v in converted])
                return column.in_(converted)
            case CriteriaOperator.NOT_IN:
                converted = self._convert_value(
                    column, value if isinstance(value, list) else [value]
                )
                if (
                    is_string
                    and converted
                    and all(isinstance(v, str) for v in converted)
                ):
                    return ~func.lower(column).in_([v.lower() for v in converted])
                return ~column.in_(converted)
            case _:
                return column == value
