"""TokenBucketRateLimiter: throttle calls to a fixed RPS using a token bucket."""

from __future__ import annotations

import threading
import time


class TokenBucketRateLimiter:
    """Thread-safe token bucket; blocks until a token is available.

    Capacity is a soft burst budget; refill_per_second is the steady rate.
    """

    def __init__(
        self, capacity: int, refill_per_second: float,
    ) -> None:
        self._capacity: float = float(capacity)
        self._refill: float = max(refill_per_second, 0.0)
        self._tokens: float = float(capacity)
        self._last: float = time.monotonic()
        self._lock: threading.Lock = threading.Lock()

    def acquire(self) -> None:
        """Block until a token is available, then consume one."""
        if self._refill <= 0.0:
            return
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(
                    self._capacity,
                    self._tokens + (now - self._last) * self._refill,
                )
                self._last = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._refill
            time.sleep(min(wait, 1.0))
