from datetime import datetime, timedelta

from app.services.subscriptions import _days_left


def test_days_left_rounds_partial_day_up() -> None:
    now = datetime(2026, 1, 1, 12, 0)
    assert _days_left(now + timedelta(days=2, seconds=1), now) == 3


def test_days_left_returns_zero_for_expired_access() -> None:
    now = datetime(2026, 1, 1, 12, 0)
    assert _days_left(now, now) == 0
    assert _days_left(now - timedelta(seconds=1), now) == 0
    assert _days_left(None, now) == 0
