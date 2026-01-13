from datetime import datetime


def make_naive(dt: datetime | None) -> datetime | None:
    """Remove timezone info from datetime for storage in timezone-naive columns."""
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt
