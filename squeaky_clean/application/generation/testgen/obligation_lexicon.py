"""Obligation lexicon: criterion/invariant phrase parsing for obligations.

The regexes and keyword tables that turn Gherkin criteria and §Notation
invariants into obligation structure. Pure functions — the projection
logic itself lives in ``project_test_obligations``.
"""

from __future__ import annotations

import re

from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind

_WHEN = re.compile(r"\bWhen\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_THEN = re.compile(r"\bThen\b(.*)$", re.IGNORECASE | re.DOTALL)
_RAISES = re.compile(r"error is raised|raise|rejected|throw|invalid", re.IGNORECASE)
_EQUALS = re.compile(
    r"result is\s+(\S+)|returns?\s+(\S+)|equals?\s+(\S+)", re.IGNORECASE)
_FIELD = re.compile(r"contain|with keys|holds|includes", re.IGNORECASE)
# An invariant is a constructor-raises duty only when it constrains a value.
# Behavioural invariants (structure, logging, wire-format) are not tested by
# constructing bad input, so they are not obligations.
_BEHAVIOURAL_INV: tuple[str, ...] = (
    "match", "publish", "implement", "uses ", "logged", "exposed", "topic",
    "field names", "verbatim", "must contain exactly",
)
_VALIDATION_INV: tuple[str, ...] = (
    "empty", "blank", "positive", "negative", "non-negative", "valid",
    "length", ">=", "<=", "> 0", "between", "at least", "at most",
    "must be", "cannot",
)


def normalize(token: str) -> str:
    """Case/underscore-insensitive key for verb matching."""
    return token.replace("_", "").lower()


def when_verb(crit: str) -> str | None:
    """The verb of a criterion's When clause, or None when absent."""
    m = _WHEN.search(crit)
    return m.group(1) if m is not None else None


def then_outcome(crit: str) -> tuple[AssertionKind, str]:
    """Assertion kind + detail parsed from a criterion's Then clause."""
    m = _THEN.search(crit)
    then = m.group(1) if m is not None else ""
    if _RAISES.search(then):
        return AssertionKind.RAISES, ""
    eq = _EQUALS.search(then)
    if eq is not None:
        return AssertionKind.EQUALS, next(g for g in eq.groups() if g)
    if _FIELD.search(then):
        return AssertionKind.FIELD_HOLDS, ""
    return AssertionKind.CALL_ONLY, ""


def is_validation_invariant(inv: str) -> bool:
    """True when the invariant constrains a value (constructor duty)."""
    low = inv.lower()
    if any(b in low for b in _BEHAVIOURAL_INV):
        return False
    return any(v in low for v in _VALIDATION_INV)
