import strawberry

from app.graphql.pos.validations.strawberry.validation_rule_types import (
    ValidationRuleResponse,
)


@strawberry.type
class ValidationRuleQueries:
    @strawberry.field()
    def validation_rules(self) -> list[ValidationRuleResponse]:
        return ValidationRuleResponse.get_all()
