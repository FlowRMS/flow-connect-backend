import strawberry

from app.graphql.campaigns.strawberry.criteria_enums import LogicalOperator
from app.graphql.campaigns.strawberry.criteria_group_input import CriteriaGroupInput


@strawberry.input
class CampaignCriteriaInput:
    """Complete criteria definition for a campaign."""

    groups: list[CriteriaGroupInput]
    group_operator: LogicalOperator = LogicalOperator.AND
