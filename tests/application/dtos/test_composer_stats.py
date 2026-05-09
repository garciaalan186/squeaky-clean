"""Tests for ComposerStats DTO (H2)."""

from __future__ import annotations

from squeaky_clean.application.dtos.composer_stats import ComposerStats


def test_default_zero() -> None:
    s = ComposerStats()
    assert s.validation_failures == 0
    assert s.manager_fallback_calls == 0
    assert s.manager_corrections_accepted == 0


def test_explicit_values() -> None:
    s = ComposerStats(
        validation_failures=3, manager_fallback_calls=2,
        manager_corrections_accepted=1,
    )
    assert s.validation_failures == 3
    assert s.manager_fallback_calls == 2
    assert s.manager_corrections_accepted == 1
