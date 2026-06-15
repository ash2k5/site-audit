"""In-process abuse controls for the public endpoints.

A single free-tier instance has no external rate limiter, so these guard the
unauthenticated trust boundary: a per-IP request rate, a global cap on
concurrent audits, and a daily ceiling on total audits to bound LLM and
Chromium spend. All limits are configurable via environment variables.
"""

import os
import threading
import time
from collections import defaultdict, deque
from datetime import date, datetime, timezone

_MAX_TRACKED_IPS = 10000


def int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


class RateLimiter:
    """Fixed sliding window of allowed requests per key (client IP)."""

    def __init__(self, max_requests: int, window_seconds: float = 60.0) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self.window
        with self._lock:
            if len(self._hits) > _MAX_TRACKED_IPS:
                self._evict(cutoff)
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True

    def _evict(self, cutoff: float) -> None:
        for key in [k for k, dq in self._hits.items() if not dq or dq[-1] <= cutoff]:
            del self._hits[key]


class DailyBudget:
    """Counts audits against a per-UTC-day ceiling."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._day: date | None = None
        self._count = 0
        self._lock = threading.Lock()

    def allow(self) -> bool:
        today = datetime.now(timezone.utc).date()
        with self._lock:
            if today != self._day:
                self._day = today
                self._count = 0
            if self._count >= self.limit:
                return False
            self._count += 1
            return True
