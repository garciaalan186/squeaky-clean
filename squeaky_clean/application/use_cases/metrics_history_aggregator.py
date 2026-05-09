"""MetricsHistoryAggregator: walk meta-eval dirs and load metrics snapshots."""

from __future__ import annotations

import json
import re
from pathlib import Path

from squeaky_clean.application.dtos.run_metrics_snapshot import RunMetricsSnapshot

_DIR_RE = re.compile(r"^meta-evaluation_(\d+)_(.+)$")


class MetricsHistoryAggregator:
    """Walk a results root for meta-eval runs and load metric snapshots."""

    def aggregate(self, results_root: Path) -> tuple[RunMetricsSnapshot, ...]:
        """Return snapshots ordered by run number; skip malformed dirs."""
        if not results_root.is_dir():
            return ()
        snapshots: list[RunMetricsSnapshot] = []
        for child in sorted(results_root.iterdir(), key=lambda p: p.name):
            snap = self._snapshot_for(child)
            if snap is not None:
                snapshots.append(snap)
        snapshots.sort(key=lambda s: s.run_number)
        return tuple(snapshots)

    def _snapshot_for(self, run_dir: Path) -> RunMetricsSnapshot | None:
        if not run_dir.is_dir():
            return None
        match = _DIR_RE.match(run_dir.name)
        if match is None:
            return None
        metrics_path = run_dir / "metrics.json"
        if not metrics_path.is_file():
            return None
        try:
            raw = json.loads(metrics_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(raw, dict):
            return None
        flat = {k: v for k, v in raw.items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)}
        return RunMetricsSnapshot(
            run_number=int(match.group(1)),
            timestamp=match.group(2),
            metrics=flat,
            problem_id=self._problem_id(run_dir),
        )

    def _problem_id(self, run_dir: Path) -> str:
        for child in sorted(run_dir.iterdir(), key=lambda p: p.name):
            if child.is_dir() and child.name.startswith("problem-set-"):
                return child.name
        return ""
