"""LifecycleTimestampLog: append squib build-lifecycle timestamps to a file."""

from __future__ import annotations

import json
import time
from pathlib import Path

_FILENAME = "squib_lifecycle.jsonl"


class LifecycleTimestampLog:
    """Append one timestamped JSON line per lifecycle milestone into a project dir."""

    def __init__(self, project_dir: Path) -> None:
        self._path: Path = project_dir / _FILENAME
        self._stamps: dict[str, float] = {}

    def record(self, event: str) -> None:
        """Append a bare milestone event stamped with the current wall-clock time."""
        self._append({"event": event})

    def record_fields(self, event: str, fields: dict[str, object]) -> None:
        """Append a milestone event carrying extra structured fields."""
        entry: dict[str, object] = {"event": event}
        entry.update(fields)
        self._append(entry)

    def elapsed_ms(self, start: str, end: str) -> int | None:
        """Whole ms between two recorded events, or None if either is absent."""
        if start not in self._stamps or end not in self._stamps:
            return None
        return int((self._stamps[end] - self._stamps[start]) * 1000)

    def _append(self, entry: dict[str, object]) -> None:
        ts = time.time()
        entry["ts"] = ts
        self._stamps[str(entry["event"])] = ts
        line = json.dumps(entry, default=str)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
