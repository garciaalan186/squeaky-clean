"""Tests for CrossModuleDependencyError: summary message and violation payload."""

import pytest

from squeaky_clean.application.generation.architecture.cross_module_dependency_error import (
    CrossModuleDependencyError,
)


def test_carries_violations_and_summarizes_counts_and_modules() -> None:
    violations = (
        "module 'Cart' depends on missing Auth::User",
        "module 'Cart' depends on missing Auth::Session",
        "module 'Billing' depends on missing Cart::Basket",
    )
    err = CrossModuleDependencyError(violations)
    assert err.violations == violations
    assert "3 cross-module dependency violations" in str(err)
    assert "across 2 module(s): ['Billing', 'Cart']" in str(err)


def test_single_violation_uses_singular_form() -> None:
    err = CrossModuleDependencyError(("module 'Cart' depends on missing X",))
    assert "1 cross-module dependency violation " in str(err)
    assert "violations" not in str(err)


def test_unparseable_violations_yield_no_module_names() -> None:
    err = CrossModuleDependencyError(("totally freeform violation text",))
    assert "across 0 module(s): []" in str(err)


def test_is_catchable_as_runtime_error() -> None:
    with pytest.raises(RuntimeError):
        raise CrossModuleDependencyError(("module 'A' has a broken dep",))
