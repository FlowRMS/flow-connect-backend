from datetime import date, timedelta
from typing import Any

# Day of week mapping (Monday = 0, Sunday = 6)
DAY_OF_WEEK_MAP = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}


def calculate_next_date(pattern: dict[str, Any], from_date: date) -> date:
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        pattern: Recurrence pattern dictionary with keys:
            - frequency: 'DAILY' | 'WEEKLY' | 'BIWEEKLY' | 'MONTHLY' | 'MONTHLY_WEEK'
            - interval: Number of periods between occurrences (default: 1)
            - dayOfWeek: Day of week for WEEKLY/BIWEEKLY/MONTHLY_WEEK (optional)
            - weekOfMonth: Week of month for MONTHLY_WEEK (optional)
            - dayOfMonth: Day of month for MONTHLY (optional)
        from_date: Starting date for calculation

    Returns:
        Next occurrence date

    Raises:
        ValueError: If pattern is invalid
    """
    frequency = pattern.get("frequency")
    interval = pattern.get("interval", 1)

    if not frequency:
        raise ValueError("Recurrence pattern must have 'frequency' field")

    if interval < 1:
        raise ValueError("Interval must be >= 1")

    # Normalize to midnight
    result = date(from_date.year, from_date.month, from_date.day)

    if frequency == "DAILY":
        return _calculate_daily(result, interval)
    elif frequency in ("WEEKLY", "BIWEEKLY"):
        return _calculate_weekly(result, pattern)
    elif frequency == "MONTHLY":
        return _calculate_monthly(result, pattern)
    elif frequency == "MONTHLY_WEEK":
        return _calculate_monthly_week(result, pattern)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def _calculate_daily(from_date: date, interval: int) -> date:
    """Calculate next occurrence for DAILY frequency."""
    return from_date + timedelta(days=interval)


def _calculate_weekly(from_date: date, pattern: dict[str, Any]) -> date:
    """
    Calculate next occurrence for WEEKLY/BIWEEKLY frequency.
    """
    frequency = pattern.get("frequency")
    interval = pattern.get("interval", 1) if frequency == "WEEKLY" else 2
    day_of_week = pattern.get("dayOfWeek", "MONDAY")

    target_day = DAY_OF_WEEK_MAP.get(day_of_week, 0)
    current_day = from_date.weekday()

    # Calculate days until next occurrence of target day
    days_to_add = (target_day - current_day) % 7
    if days_to_add == 0:
        # If today is the target day, go to next week
        days_to_add = 7

    result = from_date + timedelta(days=days_to_add)

    # If interval > 1, add additional weeks
    # But ONLY if we're scheduling future occurrences
    if interval > 1:
        result = result + timedelta(weeks=interval - 1)

    return result


def _calculate_monthly(from_date: date, pattern: dict[str, Any]) -> date:
    """
    Calculate next occurrence for MONTHLY frequency.
    """
    interval = pattern.get("interval", 1)
    day_of_month = pattern.get("dayOfMonth")

    # Use specified day or preserve original day
    target_day = day_of_month if day_of_month is not None else from_date.day

    # Move to next month(s)
    year = from_date.year
    month = from_date.month + interval

    # Handle year overflow
    while month > 12:
        month -= 12
        year += 1

    # Get last day of target month
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    last_day_of_month = (next_month - timedelta(days=1)).day

    # Use target day or last day of month (whichever is smaller)
    actual_day = min(target_day, last_day_of_month)

    return date(year, month, actual_day)


def _calculate_monthly_week(from_date: date, pattern: dict[str, Any]) -> date:
    """
    Calculate next occurrence for MONTHLY_WEEK frequency.
    (e.g., "First Monday of the month", "Last Friday of the month")
    """
    interval = pattern.get("interval", 1)
    day_of_week = pattern.get("dayOfWeek", "MONDAY")
    week_of_month = pattern.get("weekOfMonth", "FIRST")

    target_day = DAY_OF_WEEK_MAP.get(day_of_week, 0)

    # Move to next month(s)
    year = from_date.year
    month = from_date.month + interval

    # Handle year overflow
    while month > 12:
        month -= 12
        year += 1

    # Start at first day of target month
    result = date(year, month, 1)
    target_month = result.month

    if week_of_month == "LAST":
        # Find last occurrence of target day in month
        # Start from last day of month and go backwards
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        result = last_day
        while result.weekday() != target_day:
            result = result - timedelta(days=1)
            # Safety check: don't go to previous month
            if result.month != target_month:
                raise ValueError(
                    f"Could not find {day_of_week} in {week_of_month} week of month"
                )
    else:
        # Find Nth occurrence (FIRST, SECOND, THIRD, FOURTH)
        week_map = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4}
        occurrence = week_map.get(week_of_month, 1)

        count = 0
        while count < occurrence:
            if result.weekday() == target_day:
                count += 1
                if count == occurrence:
                    break
            result = result + timedelta(days=1)

            # Safety check: don't go to next month
            if result.month != target_month:
                raise ValueError(
                    f"Could not find {day_of_week} in {week_of_month} week of month"
                )

    return result


def validate_recurrence_pattern(pattern: dict[str, Any]) -> str | None:
    """
    Validate a recurrence pattern.

    Args:
        pattern: Recurrence pattern dictionary

    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(pattern, dict):
        return "Pattern must be a dictionary"

    frequency = pattern.get("frequency")
    if not frequency:
        return "Pattern must have 'frequency' field"

    valid_frequencies = ["DAILY", "WEEKLY", "BIWEEKLY", "MONTHLY", "MONTHLY_WEEK"]
    if frequency not in valid_frequencies:
        return f"Invalid frequency: {frequency}. Must be one of {valid_frequencies}"

    interval = pattern.get("interval", 1)
    if not isinstance(interval, int) or interval < 1:
        return "Interval must be an integer >= 1"

    # Validate frequency-specific fields
    if frequency in ("WEEKLY", "BIWEEKLY", "MONTHLY_WEEK"):
        day_of_week = pattern.get("dayOfWeek")
        if not day_of_week:
            return f"{frequency} frequency requires 'dayOfWeek' field"
        if day_of_week not in DAY_OF_WEEK_MAP:
            return f"Invalid dayOfWeek: {day_of_week}"

    if frequency == "MONTHLY":
        day_of_month = pattern.get("dayOfMonth")
        if day_of_month is not None:
            if not isinstance(day_of_month, int) or not (1 <= day_of_month <= 31):
                return "dayOfMonth must be an integer between 1 and 31"

    if frequency == "MONTHLY_WEEK":
        week_of_month = pattern.get("weekOfMonth")
        if not week_of_month:
            return "MONTHLY_WEEK frequency requires 'weekOfMonth' field"
        valid_weeks = ["FIRST", "SECOND", "THIRD", "FOURTH", "LAST"]
        if week_of_month not in valid_weeks:
            return f"Invalid weekOfMonth: {week_of_month}. Must be one of {valid_weeks}"

    return None


def get_recurrence_description(pattern: dict[str, Any]) -> str:
    """
    Generate a human-readable description of the recurrence pattern.

    Args:
        pattern: Recurrence pattern dictionary

    Returns:
        Human-readable description (e.g., "Every Monday", "Every 2 weeks on Friday")
    """
    frequency = pattern.get("frequency", "DAILY")
    interval = pattern.get("interval", 1)

    if frequency == "DAILY":
        if interval == 1:
            return "Every day"
        return f"Every {interval} days"

    elif frequency == "WEEKLY":
        day_of_week = pattern.get("dayOfWeek", "MONDAY")
        day_name = day_of_week.capitalize()
        if interval == 1:
            return f"Every {day_name}"
        return f"Every {interval} weeks on {day_name}"

    elif frequency == "BIWEEKLY":
        day_of_week = pattern.get("dayOfWeek", "MONDAY")
        day_name = day_of_week.capitalize()
        return f"Every 2 weeks on {day_name}"

    elif frequency == "MONTHLY":
        day_of_month = pattern.get("dayOfMonth", 1)
        if interval == 1:
            return f"Every month on day {day_of_month}"
        return f"Every {interval} months on day {day_of_month}"

    elif frequency == "MONTHLY_WEEK":
        day_of_week = pattern.get("dayOfWeek", "MONDAY")
        week_of_month = pattern.get("weekOfMonth", "FIRST")
        day_name = day_of_week.capitalize()
        week_name = week_of_month.lower()
        if interval == 1:
            return f"{week_name.capitalize()} {day_name} of every month"
        return f"{week_name.capitalize()} {day_name} every {interval} months"

    return "Unknown pattern"
