"""NotationNoveltyReporter: sidecar + triage harvest for novel Squibs (R5.5)."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.generation.notation.notation_shape_classifier import (
    NotationShapeClassifier,
)
from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[5]
_FIXTURES_DIR = _FRAMEWORK_ROOT / "eval" / "squib_fixtures"


class NotationNoveltyReporter:
    """Writes notation_novelty.json beside a run's Squib; harvests novels.

    A novel construction is observed, never a failure: the sidecar lists the
    unseen (pattern, field-usage) signatures, and the raw notation is copied
    into ``<results-root>/notation-triage/`` so it can be adopted into the
    fixture corpus deliberately (the R0.11 lesson: meet new architect shapes
    in fixtures, not in production).
    """

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        self._classifier = NotationShapeClassifier(
            fixtures_dir or _FIXTURES_DIR,
        )
        self._parser = ParseArchitectureNotation()

    def report(self, output_dir: Path, notation: str) -> int:
        """Classify ``notation``; write artifacts; return the novelty count."""
        try:
            arch = self._parser.parse(notation)
        except Exception:  # noqa: BLE001 — unparseable Squibs fail elsewhere
            return 0
        novel = self._classifier.novel_constructions(arch)
        atomic_write_text(
            output_dir / "notation_novelty.json",
            json.dumps({"count": len(novel), "novel": list(novel)}, indent=2),
        )
        if novel:
            self._harvest(output_dir, notation)
        return len(novel)

    @staticmethod
    def _harvest(output_dir: Path, notation: str) -> None:
        # output_dir = <run_dir>/problem-set-*-code -> results root is 2 up.
        triage = output_dir.parent.parent / "notation-triage"
        try:
            triage.mkdir(parents=True, exist_ok=True)
            name = f"{output_dir.parent.name}-{output_dir.name}.notation"
            (triage / name).write_text(notation)
        except OSError:
            pass  # harvesting is best-effort; the sidecar already records it
