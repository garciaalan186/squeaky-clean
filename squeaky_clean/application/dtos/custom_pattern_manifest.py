"""CustomPatternManifest DTO: one entry from a user-supplied patterns file."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CustomPatternManifestEntry:
    """One externally-supplied pattern declaration.

    name: pattern name as it appears in §Notation (e.g. ``EventSourcedAggregate``)
    icp_spec_name: spec lookup key (e.g. ``python/custom/EventSourcedAggregateICP``)
    """

    name: str
    icp_spec_name: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("CustomPatternManifestEntry.name is empty")
        if not self.icp_spec_name or not self.icp_spec_name.strip():
            raise ValueError(
                f"icp_spec_name is empty for pattern {self.name!r}"
            )


@dataclass(frozen=True)
class CustomPatternManifest:
    """Top-level manifest: list of entries plus optional spec-search roots."""

    entries: tuple[CustomPatternManifestEntry, ...]
    extra_spec_roots: tuple[str, ...] = ()
