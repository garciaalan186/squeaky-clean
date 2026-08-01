"""MCDARegistryEntry: one candidate entry from a registry JSON file."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MCDARegistryEntry:
    """One candidate entry loaded from a registry JSON file."""

    technology: str
    version_pin: str
    stability: str
    scores: dict[str, int]
