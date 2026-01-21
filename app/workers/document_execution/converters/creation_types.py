from dataclasses import dataclass, field
from uuid import UUID

from commons.db.v6.ai.entities.enums import EntityPendingType


@dataclass
class CreationIssue:
    entity_type: EntityPendingType
    dto_json: dict
    pending_entity_id: UUID | None
    error_message: str


@dataclass
class CreationResult:
    orders_created: int = 0
    invoices_created: int = 0
    credits_created: int = 0
    adjustments_created: int = 0
    issues: list[CreationIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    def has_issues_for_type(self, entity_type: EntityPendingType) -> bool:
        return any(issue.entity_type == entity_type for issue in self.issues)
