import re

from scripts.pr_review.models import ReviewContext

_PLAN_PATTERN = re.compile(r"^docs/plans/.+\.md$")
_HOTFIX_PATTERN = re.compile(r"^docs/hot-fixes/.+\.md$")
_LINEAR_TASK_PATTERN = re.compile(
    r"\*\*Linear Task\*\*:\s*\[([A-Z]+-\d+)\]"
)


def detect_plan_docs(changed_files: list[str]) -> list[str]:
    return [
        f
        for f in changed_files
        if _PLAN_PATTERN.match(f) or _HOTFIX_PATTERN.match(f)
    ]


def extract_linear_task_id(plan_content: str) -> str | None:
    match = _LINEAR_TASK_PATTERN.search(plan_content)
    return match.group(1) if match else None


def collect_context(
    plan_path: str,
    plan_content: str,
    diff: str,
    commits: str,
) -> ReviewContext:
    linear_task_id = extract_linear_task_id(plan_content)
    return ReviewContext(
        plan_path=plan_path,
        plan_content=plan_content,
        diff=diff,
        commits=commits,
        linear_task_id=linear_task_id,
        linear_task_description=None,
    )
