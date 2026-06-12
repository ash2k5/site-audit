import itertools

from site_audit import limits
from site_audit.limits import DailyBudget, RateLimiter, int_env


def test_int_env_defaults(monkeypatch):
    monkeypatch.delenv("WIDGETS", raising=False)
    assert int_env("WIDGETS", 7) == 7


def test_int_env_rejects_garbage_and_nonpositive(monkeypatch):
    monkeypatch.setenv("WIDGETS", "notanumber")
    assert int_env("WIDGETS", 7) == 7
    monkeypatch.setenv("WIDGETS", "0")
    assert int_env("WIDGETS", 7) == 7
    monkeypatch.setenv("WIDGETS", "-3")
    assert int_env("WIDGETS", 7) == 7


def test_int_env_reads_value(monkeypatch):
    monkeypatch.setenv("WIDGETS", "12")
    assert int_env("WIDGETS", 7) == 12


def test_rate_limiter_blocks_over_limit():
    rl = RateLimiter(max_requests=2)
    assert rl.allow("1.2.3.4") is True
    assert rl.allow("1.2.3.4") is True
    assert rl.allow("1.2.3.4") is False


def test_rate_limiter_is_per_key():
    rl = RateLimiter(max_requests=1)
    assert rl.allow("a") is True
    assert rl.allow("b") is True
    assert rl.allow("a") is False


def test_rate_limiter_window_rolls_off(monkeypatch):
    clock = itertools.count(0, 100)
    monkeypatch.setattr(limits.time, "monotonic", lambda: next(clock))
    rl = RateLimiter(max_requests=1, window_seconds=60)
    assert rl.allow("ip") is True
    assert rl.allow("ip") is True


def test_daily_budget_counts_and_caps():
    budget = DailyBudget(limit=2)
    assert budget.allow() is True
    assert budget.allow() is True
    assert budget.allow() is False


def test_daily_budget_resets_on_new_day(monkeypatch):
    budget = DailyBudget(limit=1)
    assert budget.allow() is True
    assert budget.allow() is False

    real_datetime = limits.datetime

    class FakeDateTime:
        @staticmethod
        def now(tz=None):
            base = real_datetime.now(tz)
            return base.replace(year=base.year + 1)

    monkeypatch.setattr(limits, "datetime", FakeDateTime)
    assert budget.allow() is True
