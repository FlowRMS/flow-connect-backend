from dataclasses import dataclass, field
from enum import Enum


class ConcernLevel(Enum):
    PASS = "pass"
    WARNING = "warning"
    CONCERN = "concern"


@dataclass
class ReviewCheck:
    name: str
    level: ConcernLevel
    notes: str


@dataclass
class ReviewResult:
    checks: list[ReviewCheck] = field(default_factory=list)

    _SEVERITY = {
        ConcernLevel.PASS: 0,
        ConcernLevel.WARNING: 1,
        ConcernLevel.CONCERN: 2,
    }

    @property
    def overall_level(self) -> ConcernLevel:
        if not self.checks:
            return ConcernLevel.PASS
        return max(self.checks, key=lambda c: self._SEVERITY[c.level]).level


@dataclass
class ReviewContext:
    plan_path: str
    plan_content: str
    diff: str
    commits: str
    linear_task_id: str | None
    linear_task_description: str | None
