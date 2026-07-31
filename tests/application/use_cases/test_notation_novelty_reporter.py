"""Tests for NotationNoveltyReporter (R5.5)."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.notation_novelty_reporter import (
    NotationNoveltyReporter,
)

_KNOWN = """MODULE M
LAYER Domain
EXPORTS [A]
DEPENDS []
CLASSES {
  A -> Strategy {
    methods: [run(): void]
    concretes: [B]
  }
}
"""

_NOVEL = """MODULE M
LAYER Domain
EXPORTS [A]
DEPENDS []
CLASSES {
  A -> Strategy {
    fields: [count: int]
    methods: [run(): void]
    invariants: ["count >= 0"]
  }
}
"""


def _reporter(tmp_path: Path) -> NotationNoveltyReporter:
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "known.squib").write_text(_KNOWN)
    return NotationNoveltyReporter(fixtures_dir=fixtures)


def _ps_dir(tmp_path: Path) -> Path:
    d = tmp_path / "results" / "meta-evaluation_001" / "problem-set-0-x-code"
    d.mkdir(parents=True)
    return d


def test_known_shape_writes_zero_sidecar_and_no_triage(tmp_path: Path) -> None:
    ps = _ps_dir(tmp_path)
    count = _reporter(tmp_path).report(ps, _KNOWN)
    assert count == 0
    payload = json.loads((ps / "notation_novelty.json").read_text())
    assert payload == {"count": 0, "novel": []}
    assert not (tmp_path / "results" / "notation-triage").exists()


def test_novel_shape_harvests_notation_for_triage(tmp_path: Path) -> None:
    ps = _ps_dir(tmp_path)
    count = _reporter(tmp_path).report(ps, _NOVEL)
    assert count == 1
    triage = tmp_path / "results" / "notation-triage"
    harvested = list(triage.glob("*.notation"))
    assert len(harvested) == 1
    assert harvested[0].read_text() == _NOVEL


def test_unparseable_notation_returns_zero(tmp_path: Path) -> None:
    ps = _ps_dir(tmp_path)
    assert _reporter(tmp_path).report(ps, "not a squib at all") == 0
    assert not (ps / "notation_novelty.json").exists()
