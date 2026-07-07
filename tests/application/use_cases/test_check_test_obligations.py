"""Tests for CheckTestObligations — deterministic obligation discharge."""

from pathlib import Path

from squeaky_clean.application.dtos.test_obligation import TestObligation
from squeaky_clean.application.use_cases.check_test_obligations import (
    CheckTestObligations,
)
from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind


def _write(tmp_path: Path, body: str) -> Path:
    (tmp_path / "test_thing.py").write_text(body)
    return tmp_path


def _raises_ob() -> TestObligation:
    return TestObligation("Ingester", "ingest_event", AssertionKind.RAISES,
                          "", "crit")


def test_call_plus_matching_assertion_is_discharged(tmp_path: Path) -> None:
    proj = _write(tmp_path,
                  "def test_x():\n    with pytest.raises(ValueError):\n"
                  "        ingest_event('')\n")
    assert CheckTestObligations().check((_raises_ob(),), proj) == ()


def test_call_without_the_assertion_kind_is_a_gap(tmp_path: Path) -> None:
    # method is called but no raises assertion -> gamed/weakened test
    proj = _write(tmp_path, "def test_x():\n    ingest_event('x')\n")
    gaps = CheckTestObligations().check((_raises_ob(),), proj)
    assert len(gaps) == 1


def test_missing_test_entirely_is_a_gap(tmp_path: Path) -> None:
    proj = _write(tmp_path, "def test_other():\n    assert 1 == 1\n")
    gaps = CheckTestObligations().check((_raises_ob(),), proj)
    assert len(gaps) == 1


def test_matching_is_naming_convention_agnostic(tmp_path: Path) -> None:
    # obligation method is snake; the test calls the camelCase form
    proj = _write(tmp_path,
                  "test('x', () => { assert.throws(() => ingestEvent('')); });")
    ob = TestObligation("Ingester", "ingest_event", AssertionKind.RAISES,
                        "", "crit")
    assert CheckTestObligations().check((ob,), proj) == ()


def test_constructor_obligation_matches_class_construction(tmp_path: Path) -> None:
    proj = _write(tmp_path,
                  "def test_x():\n    with pytest.raises(ValueError):\n"
                  "        RawBody('')\n")
    ob = TestObligation("RawBody", "<init>", AssertionKind.RAISES, "", "inv")
    assert CheckTestObligations().check((ob,), proj) == ()
