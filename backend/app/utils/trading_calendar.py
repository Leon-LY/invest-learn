"""A-share trading calendar utilities."""
from datetime import date, time


def is_a_share_trading_day(d: date) -> bool:
    """
    Check if the given date is an A-share trading day.
    Simplified check: Mon-Fri, not a weekend.
    A full implementation would use AKShare's holiday calendar.
    """
    if d.weekday() >= 5:  # Saturday or Sunday
        return False
    return True


def is_trading_hours() -> bool:
    """Check if current time is within A-share trading hours (9:30-15:00 CST)."""
    from datetime import datetime
    now = datetime.now()
    morning_start = time(9, 30)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    t = now.time()
    return (morning_start <= t <= morning_end) or (afternoon_start <= t <= afternoon_end)
