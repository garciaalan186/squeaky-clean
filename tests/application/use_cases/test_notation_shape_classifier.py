"""Tests for NotationShapeClassifier (R5.5)."""

from pathlib import Path

from squeaky_clean.application.generation.notation.notation_shape_classifier import (
    NotationShapeClassifier,
)
from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
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
  B -> Strategy {
    methods: [run(): void]
    depends: [A]
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


def _corpus(tmp_path: Path) -> Path:
    d = tmp_path / "fixtures"
    d.mkdir()
    (d / "known.squib").write_text(_KNOWN)
    return d


def test_corpus_shapes_are_not_novel(tmp_path: Path) -> None:
    classifier = NotationShapeClassifier(_corpus(tmp_path))
    arch = ParseArchitectureNotation().parse(_KNOWN)
    assert classifier.novel_constructions(arch) == ()


def test_unseen_shape_is_reported(tmp_path: Path) -> None:
    classifier = NotationShapeClassifier(_corpus(tmp_path))
    arch = ParseArchitectureNotation().parse(_NOVEL)
    novel = classifier.novel_constructions(arch)
    assert len(novel) == 1
    assert novel[0].startswith("Strategy:")


def test_empty_corpus_marks_everything_novel(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    classifier = NotationShapeClassifier(empty)
    arch = ParseArchitectureNotation().parse(_KNOWN)
    assert len(classifier.novel_constructions(arch)) == 2


def test_real_corpus_covers_its_own_shapes() -> None:
    # Self-consistency: every fixture shape is by definition known.
    fixtures = Path(__file__).resolve().parents[3] / "eval" / "squib_fixtures"
    classifier = NotationShapeClassifier(fixtures)
    parser = ParseArchitectureNotation()
    for fx in sorted(fixtures.glob("*.squib")):
        arch = parser.parse(fx.read_text())
        assert classifier.novel_constructions(arch) == (), fx.name
