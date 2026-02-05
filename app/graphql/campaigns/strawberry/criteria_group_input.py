import strawberry

from app.graphql.campaigns.strawberry.criteria_condition_input import (
    CriteriaConditionInput,
)
from app.graphql.campaigns.strawberry.criteria_enums import LogicalOperator


@strawberry.input
class CriteriaGroupInput:
    """Group of conditions with a logical operator."""

    logical_operator: LogicalOperator
    conditions: list[CriteriaConditionInput]
