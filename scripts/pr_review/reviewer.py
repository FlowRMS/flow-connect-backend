import json
import re

from scripts.pr_review.models import (
    ConcernLevel,
    ReviewCheck,
    ReviewContext,
    ReviewResult,
)

_JSON_BLOCK_PATTERN = re.compile(
    r"```(?:json)?\s*\n(.*?)\n\s*```",
    re.DOTALL,
)

_METHODOLOGY_RULES = """
## Methodology Rules

### Document Block Structure (10 mandatory blocks in order)
1. Overview / Problem+Cause+Solution
2. Design Decisions (optional)
3. Implementation Phases
4. Verification
5. Changes During Testing
6. GraphQL API Changes (optional)
7. Review
8. Changes after PR Review
9. Files Changed
10. Results

### Commit Policy (9 defined commit points)
1. Approved - Initial commit with the plan/hotfix document
2. Phase complete - After each implementation phase
3. Verification complete - After all verification steps pass
4. CDT entry complete - After each Changes During Testing fix
5. Review complete - After the review checklist is filled
6. CPR entry complete - After each Changes after PR Review fix
7. CPR re-verification - After re-executing verification post-CPR
8. CPR re-review - After re-executing review post-CPR
9. Complete - Final commit with status, dates, and Results

Commit messages must be single-line, prefixed with the document's Commit Prefix.

### Code Quality Rules
- Maximum 300 lines of code per file (excluding imports and blank lines)
- No file header comments (triple-quoted strings at file start)
- Type hints on all function parameters and return types
- Python 3.13 syntax (list[str], str | None, etc.)
- No redundant docstrings
""".strip()


def build_prompt(context: ReviewContext) -> str:
    sections = [
        "You are a code review agent for the Flow Connect project.",
        "Review this PR that contains a plan/hotfix document.",
        "",
        _METHODOLOGY_RULES,
        "",
        "## Context",
        "",
        "### Plan/Hotfix Document",
        context.plan_content,
        "",
        "### PR Diff",
        context.diff,
        "",
        "### Commit Log",
        context.commits,
    ]

    if context.linear_task_description:
        sections.extend([
            "",
            "### Linear Task Description",
            context.linear_task_description,
        ])

    sections.extend([
        "",
        "## Instructions",
        "",
        "Review the PR and respond with a JSON object:",
        '{"checks": [{"name": "...", "level": "pass|warning|concern", "notes": "..."}]}',
        "",
        "The checks must cover:",
        "1. plan_structure - block order, required blocks, correct status",
        "2. linear_alignment - plan overview matches task description",
        "3. plan_concerns - scope, complexity, edge cases, architecture",
        "4. files_match_plan - modified files in Files Changed table",
        "5. commit_policy - commit points present, correct format",
        "6. code_quality - file length, patterns, standards compliance",
    ])

    return "\n".join(sections)


def parse_response(response_text: str) -> ReviewResult:
    json_str = response_text
    match = _JSON_BLOCK_PATTERN.search(response_text)
    if match:
        json_str = match.group(1)

    data = json.loads(json_str)
    checks = [
        ReviewCheck(
            name=c["name"],
            level=ConcernLevel(c["level"]),
            notes=c["notes"],
        )
        for c in data["checks"]
    ]
    return ReviewResult(checks=checks)


def check_missing_linear_task(context: ReviewContext) -> ReviewCheck | None:
    if context.linear_task_id is None:
        return ReviewCheck(
            name="missing_linear_task",
            level=ConcernLevel.CONCERN,
            notes="No Linear task link found in plan/hotfix document",
        )
    return None


def call_claude_api(prompt: str, api_key: str) -> str:
    import anthropic  # noqa: PLC0415

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text  # type: ignore[union-attr]
