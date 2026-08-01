"""CustomPatternManifest DTO: parsed user-supplied patterns file."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.application.shared.problem.custom_pattern_manifest_entry import (
    CustomPatternManifestEntry,
)


@dataclass(frozen=True)
class CustomPatternManifest:
    """Top-level manifest: list of entries plus optional spec-search roots."""

    entries: tuple[CustomPatternManifestEntry, ...]
    extra_spec_roots: tuple[str, ...] = ()
