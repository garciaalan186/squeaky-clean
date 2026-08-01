"""CustomPatternManifestEntry: one externally-supplied pattern declaration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomPatternManifestEntry:
    """One externally-supplied pattern declaration.

    name: pattern name as it appears in §Notation (e.g. ``EventSourcedAggregate``)
    emitter_spec_name: spec lookup key (e.g. ``python/custom/EventSourcedAggregateEmitter``)
    """

    name: str
    emitter_spec_name: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("CustomPatternManifestEntry.name is empty")
        if not self.emitter_spec_name or not self.emitter_spec_name.strip():
            raise ValueError(
                f"emitter_spec_name is empty for pattern {self.name!r}"
            )
