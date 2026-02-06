from scripts.pr_review.models import ConcernLevel, ReviewCheck, ReviewResult


class TestReviewCheck:
    def test_stores_name_level_and_notes(self) -> None:
        check = ReviewCheck(
            name="plan_structure",
            level=ConcernLevel.PASS,
            notes="All blocks present",
        )
        assert check.name == "plan_structure"
        assert check.level == ConcernLevel.PASS
        assert check.notes == "All blocks present"


class TestReviewResult:
    def test_overall_level_is_pass_when_all_pass(self) -> None:
        checks = [
            ReviewCheck(name="check_1", level=ConcernLevel.PASS, notes="OK"),
            ReviewCheck(name="check_2", level=ConcernLevel.PASS, notes="OK"),
        ]
        result = ReviewResult(checks=checks)
        assert result.overall_level == ConcernLevel.PASS

    def test_overall_level_is_concern_when_any_concern(self) -> None:
        checks = [
            ReviewCheck(name="check_1", level=ConcernLevel.PASS, notes="OK"),
            ReviewCheck(name="check_2", level=ConcernLevel.CONCERN, notes="Missing block"),
        ]
        result = ReviewResult(checks=checks)
        assert result.overall_level == ConcernLevel.CONCERN

    def test_overall_level_is_warning_when_warning_and_pass(self) -> None:
        checks = [
            ReviewCheck(name="check_1", level=ConcernLevel.PASS, notes="OK"),
            ReviewCheck(name="check_2", level=ConcernLevel.WARNING, notes="Minor issue"),
        ]
        result = ReviewResult(checks=checks)
        assert result.overall_level == ConcernLevel.WARNING

    def test_concern_overrides_warning(self) -> None:
        checks = [
            ReviewCheck(name="check_1", level=ConcernLevel.WARNING, notes="Minor"),
            ReviewCheck(name="check_2", level=ConcernLevel.CONCERN, notes="Critical"),
        ]
        result = ReviewResult(checks=checks)
        assert result.overall_level == ConcernLevel.CONCERN

    def test_empty_checks_defaults_to_pass(self) -> None:
        result = ReviewResult(checks=[])
        assert result.overall_level == ConcernLevel.PASS
