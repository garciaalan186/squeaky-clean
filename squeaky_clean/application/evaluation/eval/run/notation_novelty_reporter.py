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
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger

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

    def __init__(
        self, fixtures_dir: Path | None = None,
        *, logger: RunLogger | None = None,
    ) -> None:
        self._classifier = NotationShapeClassifier(
            fixtures_dir or _FIXTURES_DIR,
        )
        self._parser = ParseArchitectureNotation()
        self._log: RunLogger = logger or NullRunLogger()

    def persist(self, output_dir: Path, notation: str) -> int:
        """Write architecture.notation + novelty artifacts; return count."""
        path = output_dir / "architecture.notation"
        atomic_write_text(path, notation)
        return self.report(output_dir, notation)

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

    def _harvest(self, output_dir: Path, notation: str) -> None:
        # output_dir = <run_dir>/problem-set-*-code -> results root is 2 up.
        triage = output_dir.parent.parent / "notation-triage"
        name = f"{output_dir.parent.name}-{output_dir.name}.notation"
        try:
            atomic_write_text(triage / name, notation)
        except OSError as exc:
            # Best-effort (the sidecar already records it) — but logged (R6.8).
            self._log.event("notation_triage_write_failed",
                            path=str(triage / name), error=str(exc))
