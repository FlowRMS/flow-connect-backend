from scripts.pr_review.collector import (
    collect_context,
    detect_plan_docs,
    extract_linear_task_id,
)
from scripts.pr_review.models import ReviewContext


class TestDetectPlanDocs:
    def test_finds_plan_docs(self) -> None:
        changed_files = [
            "app/some_file.py",
            "docs/plans/2026-02/2026-02-05-01-some-plan.md",
            "tests/test_something.py",
        ]
        result = detect_plan_docs(changed_files)
        assert result == ["docs/plans/2026-02/2026-02-05-01-some-plan.md"]

    def test_finds_hotfix_docs(self) -> None:
        changed_files = [
            "app/some_file.py",
            "docs/hot-fixes/2026-02/2026-02-05-01-some-fix.md",
        ]
        result = detect_plan_docs(changed_files)
        assert result == ["docs/hot-fixes/2026-02/2026-02-05-01-some-fix.md"]

    def test_finds_both_plan_and_hotfix(self) -> None:
        changed_files = [
            "docs/plans/2026-02/2026-02-05-01-some-plan.md",
            "docs/hot-fixes/2026-02/2026-02-05-01-some-fix.md",
        ]
        result = detect_plan_docs(changed_files)
        assert len(result) == 2

    def test_returns_empty_when_no_docs(self) -> None:
        changed_files = ["app/some_file.py", "tests/test_something.py"]
        result = detect_plan_docs(changed_files)
        assert result == []

    def test_ignores_non_md_files_in_plan_dirs(self) -> None:
        changed_files = [
            "docs/plans/2026-02/image.png",
            "docs/plans/2026-02/2026-02-05-01-plan.md",
        ]
        result = detect_plan_docs(changed_files)
        assert result == ["docs/plans/2026-02/2026-02-05-01-plan.md"]


class TestExtractLinearTaskId:
    def test_extracts_task_id_from_plan_header(self) -> None:
        content = (
            "# Some Plan\n\n"
            "- **Status**: 🔵 Approved\n"
            "- **Linear Task**: [FLO-1234](https://linear.app/flow-labs/issue/FLO-1234/some-task)\n"
            "- **Created**: 2026-02-05\n"
        )
        result = extract_linear_task_id(content)
        assert result == "FLO-1234"

    def test_returns_none_when_no_linear_task(self) -> None:
        content = (
            "# Some Plan\n\n"
            "- **Status**: 🔵 Approved\n"
            "- **Created**: 2026-02-05\n"
        )
        result = extract_linear_task_id(content)
        assert result is None

    def test_extracts_different_task_numbers(self) -> None:
        content = "- **Linear Task**: [FLO-999](https://linear.app/flow-labs/issue/FLO-999/task)\n"
        result = extract_linear_task_id(content)
        assert result == "FLO-999"

    def test_returns_none_when_linear_task_line_empty(self) -> None:
        content = "- **Linear Task**:\n- **Created**: 2026-02-05\n"
        result = extract_linear_task_id(content)
        assert result is None


class TestCollectContext:
    def test_builds_review_context_with_linear_task(self) -> None:
        plan_content = (
            "# Some Plan\n\n"
            "- **Linear Task**: [FLO-1234](https://linear.app/flow-labs/issue/FLO-1234/task)\n"
        )
        result = collect_context(
            plan_path="docs/plans/2026-02/plan.md",
            plan_content=plan_content,
            diff="some diff content",
            commits="abc1234 Phase 1 complete",
        )
        assert isinstance(result, ReviewContext)
        assert result.plan_path == "docs/plans/2026-02/plan.md"
        assert result.plan_content == plan_content
        assert result.diff == "some diff content"
        assert result.commits == "abc1234 Phase 1 complete"
        assert result.linear_task_id == "FLO-1234"

    def test_builds_review_context_without_linear_task(self) -> None:
        plan_content = "# Some Plan\n\n- **Status**: 🔵 Approved\n"
        result = collect_context(
            plan_path="docs/plans/2026-02/plan.md",
            plan_content=plan_content,
            diff="diff",
            commits="commits",
        )
        assert result.linear_task_id is None
