"""Tests for ConventionToInvariant lookup."""

import pytest

from squeaky_clean.application.use_cases.convention_to_invariant import (
    ConventionToInvariant,
    UnknownConventionError,
)


def test_lookup_known_tag_returns_text() -> None:
    c = ConventionToInvariant()
    text = c.lookup("timeline_includes_self")
    assert "user's own posts" in text


def test_lookup_unknown_tag_raises() -> None:
    c = ConventionToInvariant()
    with pytest.raises(UnknownConventionError):
        c.lookup("not_a_real_tag")


def test_lookup_all_seeded_tags() -> None:
    c = ConventionToInvariant()
    for tag in (
        "timeline_includes_self", "follow_asymmetric",
        "auth_session_single_active", "unique_by_natural_key",
        "soft_delete_preserves_history", "idempotent_retries_safe",
    ):
        assert c.lookup(tag)
