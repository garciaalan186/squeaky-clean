"""Tests for ProblemResolver."""

import pytest

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver


def test_resolves_p0_to_the_python_calculator_spec() -> None:
    spec = ProblemResolver().resolve("P0")
    assert spec.id == "P0"
    assert spec.target_language is TargetLanguage.PYTHON


def test_resolves_language_variant_ids() -> None:
    resolver = ProblemResolver()
    assert resolver.resolve("P0JS").target_language is TargetLanguage.JAVASCRIPT
    assert resolver.resolve("P0JAVA").target_language is TargetLanguage.JAVA


def test_registry_ids_are_self_consistent() -> None:
    resolver = ProblemResolver()
    for pid in ("P1", "P6", "P11"):
        assert resolver.resolve(pid).id == pid


def test_unknown_id_raises_key_error_naming_the_id() -> None:
    with pytest.raises(KeyError, match="unknown problem id: P99"):
        ProblemResolver().resolve("P99")
