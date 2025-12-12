"""GraphQL input types for campaign criteria."""

from enum import Enum

import strawberry

from app.graphql.links.models.entity_type import EntityType


@strawberry.enum
class CriteriaOperator(Enum):
    """Operators for criteria conditions."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUALS = "greater_than_or_equals"
    LESS_THAN_OR_EQUALS = "less_than_or_equals"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    IN = "in"
    NOT_IN = "not_in"


@strawberry.enum
class LogicalOperator(Enum):
    """Logical operators for combining conditions."""

    AND = "and"
    OR = "or"


@strawberry.input
class CriteriaConditionInput:
    """Single condition for filtering records."""

    entity_type: EntityType
    field: str
    operator: CriteriaOperator
    value: strawberry.scalars.JSON | None = None


@strawberry.input
class CriteriaGroupInput:
    """Group of conditions with a logical operator."""

    logical_operator: LogicalOperator
    conditions: list[CriteriaConditionInput]


@strawberry.input
class CampaignCriteriaInput:
    """Complete criteria definition for a campaign."""

    groups: list[CriteriaGroupInput]
    group_operator: LogicalOperator = LogicalOperator.AND
