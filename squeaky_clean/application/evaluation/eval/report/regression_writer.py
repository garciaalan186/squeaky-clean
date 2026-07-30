"""RegressionWriter: persist RegressionRecord list to eval/reports/regressions.json."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.evaluation.eval.report.regression_record import RegressionRecord
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text


class RegressionWriter:
    """Append regression records to a JSON file under eval/reports/."""

    def write(
        self, records: Sequence[RegressionRecord], target: Path,
    ) -> None:
        """Append the supplied records to ``target`` as a JSON array."""
        existing: list[dict[str, object]] = []
        if target.exists():
            try:
                loaded = json.loads(target.read_text())
                if isinstance(loaded, list):
                    existing = [r for r in loaded if isinstance(r, dict)]
            except json.JSONDecodeError:
                existing = []
        existing.extend(asdict(r) for r in records)
        atomic_write_text(target, json.dumps(existing, indent=2))
