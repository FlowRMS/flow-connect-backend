from unittest.mock import MagicMock, patch

from scripts.pr_review.models import ConcernLevel, ReviewCheck, ReviewResult
from scripts.pr_review.notifier import (
    determine_linear_action,
    format_pr_comment,
    resolve_linear_issue,
    resolve_linear_state,
)


class TestFormatPrComment:
    def test_includes_review_header(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="plan_structure", level=ConcernLevel.PASS, notes="OK"),
        ])
        comment = format_pr_comment(result)
        assert "PR Plan Review" in comment

    def test_includes_check_names_and_notes(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(
                name="plan_structure",
                level=ConcernLevel.PASS,
                notes="All blocks present",
            ),
            ReviewCheck(
                name="code_quality",
                level=ConcernLevel.WARNING,
                notes="File too long",
            ),
        ])
        comment = format_pr_comment(result)
        assert "plan_structure" in comment
        assert "code_quality" in comment
        assert "All blocks present" in comment

    def test_includes_concern_level_icons(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.PASS, notes="OK"),
            ReviewCheck(name="c2", level=ConcernLevel.WARNING, notes="Minor"),
            ReviewCheck(name="c3", level=ConcernLevel.CONCERN, notes="Critical"),
        ])
        comment = format_pr_comment(result)
        assert ":green_circle:" in comment
        assert ":yellow_circle:" in comment
        assert ":red_circle:" in comment

    def test_includes_overall_recommendation(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.CONCERN, notes="Issue"),
        ])
        comment = format_pr_comment(result)
        assert ":red_circle:" in comment


class TestDetermineLinearAction:
    def test_pass_targets_ready_to_merge(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.PASS, notes="OK"),
        ])
        action = determine_linear_action(result)
        assert action.target_status == "Ready to merge to staging"

    def test_warning_targets_ready_to_merge(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.WARNING, notes="Minor"),
        ])
        action = determine_linear_action(result)
        assert action.target_status == "Ready to merge to staging"

    def test_concern_targets_todo(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.CONCERN, notes="Critical"),
        ])
        action = determine_linear_action(result)
        assert action.target_status == "Todo"

    def test_action_has_non_empty_comment(self) -> None:
        result = ReviewResult(checks=[
            ReviewCheck(name="c1", level=ConcernLevel.PASS, notes="OK"),
        ])
        action = determine_linear_action(result)
        assert len(action.comment) > 0


class TestResolveLinearIssue:
    @patch("scripts.pr_review.notifier.httpx.post")
    def test_returns_issue_id_and_team_id(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "issue": {"id": "uuid-123", "team": {"id": "team-456"}},
            },
        }
        mock_post.return_value = mock_response

        result = resolve_linear_issue("FLO-1234", "api-key")
        assert result == ("uuid-123", "team-456")

    @patch("scripts.pr_review.notifier.httpx.post")
    def test_returns_none_when_not_found(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"issue": None},
        }
        mock_post.return_value = mock_response

        result = resolve_linear_issue("FLO-9999", "api-key")
        assert result is None


class TestResolveLinearState:
    @patch("scripts.pr_review.notifier.httpx.post")
    def test_returns_state_id(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"workflowStates": {"nodes": [{"id": "state-789"}]}},
        }
        mock_post.return_value = mock_response

        result = resolve_linear_state("team-456", "Todo", "api-key")
        assert result == "state-789"

    @patch("scripts.pr_review.notifier.httpx.post")
    def test_returns_none_when_not_found(self, mock_post: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {"workflowStates": {"nodes": []}},
        }
        mock_post.return_value = mock_response

        result = resolve_linear_state("team-456", "Unknown", "api-key")
        assert result is None
