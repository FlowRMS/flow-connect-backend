"""
Unit tests for recurrence_utils module.

These tests validate the recurrence calculation logic to ensure it matches
the frontend implementation and handles all edge cases correctly.
"""

import pytest
from datetime import date, timedelta
from app.graphql.v2.core.deliveries.utils.recurrence_utils import (
    calculate_next_date,
    validate_recurrence_pattern,
    get_recurrence_description,
)


class TestCalculateNextDate:
    """Test cases for calculate_next_date function."""

    # DAILY tests
    def test_daily_simple(self):
        """Test daily recurrence with interval=1."""
        pattern = {"frequency": "DAILY", "interval": 1}
        from_date = date(2024, 1, 15)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 1, 16)

    def test_daily_interval_3(self):
        """Test daily recurrence with interval=3."""
        pattern = {"frequency": "DAILY", "interval": 3}
        from_date = date(2024, 1, 15)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 1, 18)

    def test_weekly_same_day(self):
        """Test weekly on same day - should go to next week."""
        pattern = {"frequency": "WEEKLY", "interval": 1, "dayOfWeek": "MONDAY"}
        from_date = date(2024, 1, 22)  # Monday
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 1, 29)  # Next Monday

    def test_weekly_next_day(self):
        """Test weekly from Saturday to Monday."""
        pattern = {"frequency": "WEEKLY", "interval": 1, "dayOfWeek": "MONDAY"}
        from_date = date(2024, 1, 20)  # Saturday
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 1, 22)  # Next Monday (2 days)

    def test_weekly_interval_2(self):
        """Test weekly with interval=2 (every 2 weeks)."""
        pattern = {"frequency": "WEEKLY", "interval": 2, "dayOfWeek": "FRIDAY"}
        from_date = date(2024, 1, 20)  # Saturday
        result = calculate_next_date(pattern, from_date)
        # Should be Friday (26th), then add 1 more week = Feb 2
        assert result == date(2024, 2, 2)

    def test_biweekly(self):
        """Test BIWEEKLY frequency."""
        pattern = {"frequency": "BIWEEKLY", "dayOfWeek": "WEDNESDAY"}
        from_date = date(2024, 1, 15)  # Monday
        result = calculate_next_date(pattern, from_date)
        # Next Wednesday is 17th, then add 1 week = 24th
        assert result == date(2024, 1, 24)

    def test_monthly_with_day_of_month(self):
        """Test monthly with specific day of month."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 15}
        from_date = date(2024, 1, 31)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 2, 15)

    def test_monthly_without_day_of_month(self):
        """Test monthly without dayOfMonth - should preserve original day."""
        pattern = {"frequency": "MONTHLY", "interval": 1}
        from_date = date(2024, 1, 15)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 2, 15)  # Preserves day 15

    def test_monthly_end_of_month(self):
        """Test monthly on day 31 going to February (clamps to 29 in leap year)."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 31}
        from_date = date(2024, 1, 31)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 2, 29)  # 2024 is leap year

    def test_monthly_end_of_month_non_leap(self):
        """Test monthly on day 31 going to February in non-leap year."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 31}
        from_date = date(2023, 1, 31)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2023, 2, 28)  # 2023 is not leap year

    def test_monthly_interval_2(self):
        """Test monthly with interval=2 (every 2 months)."""
        pattern = {"frequency": "MONTHLY", "interval": 2, "dayOfMonth": 15}
        from_date = date(2024, 1, 15)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 3, 15)

    def test_monthly_year_wrap(self):
        """Test monthly going from December to January."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 15}
        from_date = date(2023, 12, 15)
        result = calculate_next_date(pattern, from_date)
        assert result == date(2024, 1, 15)

    def test_monthly_week_first_monday(self):
        """Test first Monday of the month."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "MONDAY",
            "weekOfMonth": "FIRST",
        }
        from_date = date(2024, 1, 30)
        result = calculate_next_date(pattern, from_date)
        # First Monday of February 2024 is the 5th
        assert result == date(2024, 2, 5)

    def test_monthly_week_last_friday(self):
        """Test last Friday of the month."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "FRIDAY",
            "weekOfMonth": "LAST",
        }
        from_date = date(2024, 1, 26)  # Last Friday of January
        result = calculate_next_date(pattern, from_date)
        # Last Friday of February 2024 is the 23rd
        assert result == date(2024, 2, 23)

    def test_monthly_week_second_wednesday(self):
        """Test second Wednesday of the month."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "WEDNESDAY",
            "weekOfMonth": "SECOND",
        }
        from_date = date(2024, 1, 15)
        result = calculate_next_date(pattern, from_date)
        # Second Wednesday of February 2024 is the 14th
        assert result == date(2024, 2, 14)

    def test_monthly_week_fourth_thursday(self):
        """Test fourth Thursday of the month."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "THURSDAY",
            "weekOfMonth": "FOURTH",
        }
        from_date = date(2024, 1, 25)
        result = calculate_next_date(pattern, from_date)
        # Fourth Thursday of February 2024 is the 22nd
        assert result == date(2024, 2, 22)

    def test_invalid_frequency(self):
        """Test with invalid frequency."""
        pattern = {"frequency": "INVALID", "interval": 1}
        from_date = date(2024, 1, 15)
        with pytest.raises(ValueError, match="Unknown frequency"):
            calculate_next_date(pattern, from_date)

    def test_missing_frequency(self):
        """Test with missing frequency."""
        pattern = {"interval": 1}
        from_date = date(2024, 1, 15)
        with pytest.raises(ValueError, match="must have 'frequency' field"):
            calculate_next_date(pattern, from_date)

    def test_interval_less_than_1(self):
        """Test with interval < 1."""
        pattern = {"frequency": "DAILY", "interval": 0}
        from_date = date(2024, 1, 15)
        with pytest.raises(ValueError, match="Interval must be >= 1"):
            calculate_next_date(pattern, from_date)


class TestValidateRecurrencePattern:
    """Test cases for validate_recurrence_pattern function."""

    def test_valid_daily(self):
        """Test valid DAILY pattern."""
        pattern = {"frequency": "DAILY", "interval": 1}
        assert validate_recurrence_pattern(pattern) is None

    def test_valid_weekly(self):
        """Test valid WEEKLY pattern."""
        pattern = {"frequency": "WEEKLY", "interval": 1, "dayOfWeek": "MONDAY"}
        assert validate_recurrence_pattern(pattern) is None

    def test_valid_monthly(self):
        """Test valid MONTHLY pattern."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 15}
        assert validate_recurrence_pattern(pattern) is None

    def test_valid_monthly_week(self):
        """Test valid MONTHLY_WEEK pattern."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "FRIDAY",
            "weekOfMonth": "LAST",
        }
        assert validate_recurrence_pattern(pattern) is None

    def test_invalid_not_dict(self):
        """Test with non-dict pattern."""
        pattern = "not a dict"
        error = validate_recurrence_pattern(pattern)
        assert "must be a dictionary" in error

    def test_invalid_missing_frequency(self):
        """Test with missing frequency."""
        pattern = {"interval": 1}
        error = validate_recurrence_pattern(pattern)
        assert "must have 'frequency' field" in error

    def test_invalid_frequency_value(self):
        """Test with invalid frequency value."""
        pattern = {"frequency": "INVALID", "interval": 1}
        error = validate_recurrence_pattern(pattern)
        assert "Invalid frequency" in error

    def test_invalid_interval_not_int(self):
        """Test with non-integer interval."""
        pattern = {"frequency": "DAILY", "interval": "not an int"}
        error = validate_recurrence_pattern(pattern)
        assert "Interval must be an integer" in error

    def test_invalid_interval_zero(self):
        """Test with interval=0."""
        pattern = {"frequency": "DAILY", "interval": 0}
        error = validate_recurrence_pattern(pattern)
        assert "Interval must be an integer >= 1" in error

    def test_weekly_missing_day_of_week(self):
        """Test WEEKLY without dayOfWeek."""
        pattern = {"frequency": "WEEKLY", "interval": 1}
        error = validate_recurrence_pattern(pattern)
        assert "requires 'dayOfWeek' field" in error

    def test_weekly_invalid_day_of_week(self):
        """Test WEEKLY with invalid dayOfWeek."""
        pattern = {"frequency": "WEEKLY", "interval": 1, "dayOfWeek": "INVALID"}
        error = validate_recurrence_pattern(pattern)
        assert "Invalid dayOfWeek" in error

    def test_monthly_invalid_day_of_month(self):
        """Test MONTHLY with invalid dayOfMonth."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 32}
        error = validate_recurrence_pattern(pattern)
        assert "dayOfMonth must be an integer between 1 and 31" in error

    def test_monthly_week_missing_week_of_month(self):
        """Test MONTHLY_WEEK without weekOfMonth."""
        pattern = {"frequency": "MONTHLY_WEEK", "interval": 1, "dayOfWeek": "MONDAY"}
        error = validate_recurrence_pattern(pattern)
        assert "requires 'weekOfMonth' field" in error

    def test_monthly_week_invalid_week_of_month(self):
        """Test MONTHLY_WEEK with invalid weekOfMonth."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "MONDAY",
            "weekOfMonth": "INVALID",
        }
        error = validate_recurrence_pattern(pattern)
        assert "Invalid weekOfMonth" in error


class TestGetRecurrenceDescription:
    """Test cases for get_recurrence_description function."""

    def test_daily_every_day(self):
        """Test description for DAILY with interval=1."""
        pattern = {"frequency": "DAILY", "interval": 1}
        assert get_recurrence_description(pattern) == "Every day"

    def test_daily_every_3_days(self):
        """Test description for DAILY with interval=3."""
        pattern = {"frequency": "DAILY", "interval": 3}
        assert get_recurrence_description(pattern) == "Every 3 days"

    def test_weekly_every_monday(self):
        """Test description for WEEKLY every Monday."""
        pattern = {"frequency": "WEEKLY", "interval": 1, "dayOfWeek": "MONDAY"}
        assert get_recurrence_description(pattern) == "Every Monday"

    def test_weekly_every_2_weeks(self):
        """Test description for WEEKLY with interval=2."""
        pattern = {"frequency": "WEEKLY", "interval": 2, "dayOfWeek": "FRIDAY"}
        assert get_recurrence_description(pattern) == "Every 2 weeks on Friday"

    def test_biweekly(self):
        """Test description for BIWEEKLY."""
        pattern = {"frequency": "BIWEEKLY", "dayOfWeek": "WEDNESDAY"}
        assert get_recurrence_description(pattern) == "Every 2 weeks on Wednesday"

    def test_monthly_every_month(self):
        """Test description for MONTHLY with interval=1."""
        pattern = {"frequency": "MONTHLY", "interval": 1, "dayOfMonth": 15}
        assert get_recurrence_description(pattern) == "Every month on day 15"

    def test_monthly_every_2_months(self):
        """Test description for MONTHLY with interval=2."""
        pattern = {"frequency": "MONTHLY", "interval": 2, "dayOfMonth": 1}
        assert get_recurrence_description(pattern) == "Every 2 months on day 1"

    def test_monthly_week_first_monday(self):
        """Test description for MONTHLY_WEEK first Monday."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "MONDAY",
            "weekOfMonth": "FIRST",
        }
        assert get_recurrence_description(pattern) == "First Monday of every month"

    def test_monthly_week_last_friday(self):
        """Test description for MONTHLY_WEEK last Friday."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 1,
            "dayOfWeek": "FRIDAY",
            "weekOfMonth": "LAST",
        }
        assert get_recurrence_description(pattern) == "Last Friday of every month"

    def test_monthly_week_with_interval(self):
        """Test description for MONTHLY_WEEK with interval=2."""
        pattern = {
            "frequency": "MONTHLY_WEEK",
            "interval": 2,
            "dayOfWeek": "THURSDAY",
            "weekOfMonth": "THIRD",
        }
        assert get_recurrence_description(pattern) == "Third Thursday every 2 months"
