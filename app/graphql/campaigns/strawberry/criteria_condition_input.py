import strawberry
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.campaigns.strawberry.criteria_enums import CriteriaOperator


@strawberry.input
class CriteriaConditionInput:
    """Single condition for filtering records."""

    entity_type: EntityType
    field: str
    operator: CriteriaOperator
    value: strawberry.scalars.JSON | None = None
