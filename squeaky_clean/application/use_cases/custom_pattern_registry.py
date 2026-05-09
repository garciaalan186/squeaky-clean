"""CustomPatternRegistry: register external GoF/DDD pattern variants at runtime."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomPattern:
    """One externally-supplied pattern: name + ICP spec stem."""

    name: str
    icp_spec_name: str


class CustomPatternRegistry:
    """Mutable registry of pattern names → ICP spec names.

    Built-ins (Strategy, Repository, Entity, ...) live in the spec library
    and are resolved by AssignPatterns directly. Externally-supplied
    patterns register via ``register(...)`` and are resolved through the
    same registry, allowing domain-specific patterns (e.g.
    EventSourcedAggregate) without modifying core.
    """

    def __init__(self) -> None:
        self._patterns: dict[str, CustomPattern] = {}

    def register(self, pattern: CustomPattern) -> None:
        """Add a CustomPattern. Existing names are overwritten."""
        self._patterns[pattern.name] = pattern

    def lookup(self, pattern_name: str) -> CustomPattern | None:
        """Return the CustomPattern registered under ``pattern_name`` or None."""
        return self._patterns.get(pattern_name)

    def all(self) -> Mapping[str, CustomPattern]:
        """Return read-only view of every registered pattern."""
        return dict(self._patterns)
