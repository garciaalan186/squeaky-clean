"""MetricsHistoryAggregator: walk meta-eval dirs and load metrics snapshots."""

from __future__ import annotations

import json
import re
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.run_metrics_snapshot import RunMetricsSnapshot
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger

_DIR_RE = re.compile(r"^meta-evaluation_(\d+)_(.+)$")


class MetricsHistoryAggregator:
    """Walk a results root for meta-eval runs and load metric snapshots."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._log: RunLogger = logger or NullRunLogger()

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
        except (OSError, json.JSONDecodeError) as exc:
            self._log.event("metrics_snapshot_skipped",
                            path=str(metrics_path), error=str(exc))
            return None
        if not isinstance(raw, dict):
            return None
        return RunMetricsSnapshot(
            run_number=int(match.group(1)),
            timestamp=match.group(2),
            metrics=self._flatten(raw),
            problem_id=self._problem_id(run_dir),
        )

    def _flatten(self, raw: dict[str, object]) -> dict[str, float | int]:
        """Flatten schema-v2 value objects to their v1 leaf names — every
        leaf was a unique flat field in v1, so old and new metrics.json yield
        identical keys. ``cache_by_tier`` skipped (its per-tier leaves
        collide); top-level scalars win."""
        flat: dict[str, float | int] = {}
        for key, value in raw.items():
            if key == "cache_by_tier" or not isinstance(value, dict):
                continue
            for leaf, scalar in value.items():
                if isinstance(scalar, (int, float)) and not isinstance(
                    scalar, bool,
                ):
                    flat[leaf] = scalar
        for key, value in raw.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                flat[key] = value
        return flat

    def _problem_id(self, run_dir: Path) -> str:
        for child in sorted(run_dir.iterdir(), key=lambda p: p.name):
            if child.is_dir() and child.name.startswith("problem-set-"):
                return child.name
        return ""
