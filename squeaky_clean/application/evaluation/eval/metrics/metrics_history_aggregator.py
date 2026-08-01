"""MetricsHistoryAggregator: walk meta-eval dirs and load metrics snapshots."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.run_metrics_snapshot import RunMetricsSnapshot

_DIR_RE = re.compile(r"^meta-evaluation_(\d+)_(.+)$")
_LOG = logging.getLogger(__name__)


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
        except (OSError, json.JSONDecodeError) as exc:
            _LOG.warning("skipping unreadable %s: %s", metrics_path, exc)
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
        """Flatten schema-v2 value-object payloads to their v1 leaf names.

        Every leaf name was a unique flat field in schema v1, so promoting
        nested scalars restores the exact historical key set — old and new
        metrics.json files yield identical snapshot keys. ``cache_by_tier``
        is skipped (its per-tier leaves collide); top-level scalars win.
        """
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
