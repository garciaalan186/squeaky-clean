"""Unit tests for TokenBucketRateLimiter."""

import time

from squeaky_clean.infrastructure.llm.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)


def test_zero_refill_disables_limiter() -> None:
    limiter = TokenBucketRateLimiter(capacity=1, refill_per_second=0.0)
    start = time.monotonic()
    for _ in range(100):
        limiter.acquire()
    assert time.monotonic() - start < 0.5


def test_burst_consumes_capacity_then_throttles() -> None:
    limiter = TokenBucketRateLimiter(capacity=3, refill_per_second=10.0)
    start = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    burst_elapsed = time.monotonic() - start
    assert burst_elapsed < 0.05
    limiter.acquire()
    total = time.monotonic() - start
    assert total >= 0.05
