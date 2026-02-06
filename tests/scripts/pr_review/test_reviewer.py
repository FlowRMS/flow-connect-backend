import json

from scripts.pr_review.models import ConcernLevel, ReviewContext
from scripts.pr_review.reviewer import (
    build_prompt,
    check_missing_linear_task,
    parse_response,
)


def _make_context(**overrides: object) -> ReviewContext:
    defaults: dict[str, object] = {
        "plan_path": "docs/plans/2026-02/plan.md",
        "plan_content": "# Test Plan\n\nSome content",
        "diff": "diff --git a/file.py b/file.py\n+new line",
        "commits": "abc1234 Phase 1 complete",
        "linear_task_id": "FLO-1234",
        "linear_task_description": "Task description here",
    }
    defaults.update(overrides)
    return ReviewContext(**defaults)  # type: ignore[arg-type]


class TestBuildPrompt:
    def test_includes_plan_content(self) -> None:
        context = _make_context(plan_content="# My Special Plan\n\nDetails here")
        prompt = build_prompt(context)
        assert "# My Special Plan" in prompt

    def test_includes_diff(self) -> None:
        context = _make_context(diff="diff --git important change")
        prompt = build_prompt(context)
        assert "diff --git important change" in prompt

    def test_includes_commits(self) -> None:
        context = _make_context(commits="abc1234 Phase 1 complete")
        prompt = build_prompt(context)
        assert "abc1234 Phase 1 complete" in prompt

    def test_includes_methodology_rules(self) -> None:
        context = _make_context()
        prompt = build_prompt(context)
        assert "block" in prompt.lower()
        assert "commit" in prompt.lower()

    def test_requests_json_response_format(self) -> None:
        context = _make_context()
        prompt = build_prompt(context)
        assert "json" in prompt.lower()

    def test_includes_linear_task_description_when_present(self) -> None:
        context = _make_context(linear_task_description="Build a login page")
        prompt = build_prompt(context)
        assert "Build a login page" in prompt

    def test_excludes_linear_task_section_when_none(self) -> None:
        context = _make_context(linear_task_description=None)
        prompt = build_prompt(context)
        assert "Linear Task Description" not in prompt


class TestParseResponse:
    def test_parses_json_checks_to_review_result(self) -> None:
        response = json.dumps({
            "checks": [
                {"name": "plan_structure", "level": "pass", "notes": "All blocks present"},
                {"name": "code_quality", "level": "warning", "notes": "File near limit"},
            ],
        })
        result = parse_response(response)
        assert len(result.checks) == 2
        assert result.checks[0].name == "plan_structure"
        assert result.checks[0].level == ConcernLevel.PASS
        assert result.checks[1].level == ConcernLevel.WARNING

    def test_parses_concern_level(self) -> None:
        response = json.dumps({
            "checks": [
                {"name": "commit_policy", "level": "concern", "notes": "Missing commits"},
            ],
        })
        result = parse_response(response)
        assert result.checks[0].level == ConcernLevel.CONCERN

    def test_parses_json_from_markdown_code_block(self) -> None:
        response = (
            '```json\n'
            '{"checks": [{"name": "test", "level": "pass", "notes": "OK"}]}\n'
            '```'
        )
        result = parse_response(response)
        assert len(result.checks) == 1
        assert result.checks[0].name == "test"


class TestCheckMissingLinearTask:
    def test_returns_concern_when_no_task(self) -> None:
        context = _make_context(
            linear_task_id=None,
            linear_task_description=None,
        )
        check = check_missing_linear_task(context)
        assert check is not None
        assert check.level == ConcernLevel.CONCERN

    def test_returns_none_when_task_present(self) -> None:
        context = _make_context(linear_task_id="FLO-1234")
        check = check_missing_linear_task(context)
        assert check is None
