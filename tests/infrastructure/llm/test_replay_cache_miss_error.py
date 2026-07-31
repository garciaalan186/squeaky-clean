"""Tests for ReplayCacheMissError (R5.7)."""

from squeaky_clean.infrastructure.llm.replay_cache_miss_error import (
    ReplayCacheMissError,
)


def test_is_a_runtime_error() -> None:
    assert issubclass(ReplayCacheMissError, RuntimeError)
