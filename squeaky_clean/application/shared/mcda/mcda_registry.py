"""MCDARegistry: loads MCDA candidate score files from eval/mcda_scores/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast


class MCDARegistryEntryMissingError(KeyError):
    """Raised when a category has no registered candidates on disk."""


@dataclass(frozen=True)
class MCDARegistryEntry:
    """One candidate entry loaded from a registry JSON file."""

    technology: str
    version_pin: str
    stability: str
    scores: dict[str, int]


class MCDARegistry:
    """Filesystem-backed registry of per-category MCDA candidate scores."""

    def __init__(self, root: Path) -> None:
        self._root: Path = root

    def candidates(self, category: str) -> tuple[MCDARegistryEntry, ...]:
        """Return parsed candidates for ``category`` (frozen entries)."""
        path = self._root / f"{category}.json"
        if not path.is_file():
            raise MCDARegistryEntryMissingError(
                f"no MCDA registry file for category={category!r} at {path}"
            )
        raw = cast(dict[str, object], json.loads(path.read_text()))
        rows = cast(list[dict[str, object]], raw.get("candidates") or [])
        return tuple(self._row(r) for r in rows)

    @staticmethod
    def _row(r: dict[str, object]) -> MCDARegistryEntry:
        scores_raw = cast(dict[str, int], r.get("scores") or {})
        return MCDARegistryEntry(
            technology=str(r.get("technology") or ""),
            version_pin=str(r.get("version_pin") or ""),
            stability=str(r.get("stability") or "ga"),
            scores={str(k): int(v) for k, v in scores_raw.items()},
        )
