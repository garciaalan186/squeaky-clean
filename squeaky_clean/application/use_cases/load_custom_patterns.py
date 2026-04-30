"""LoadCustomPatterns: read a JSON manifest of custom GoF/DDD patterns."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.dtos.custom_pattern_manifest import (
    CustomPatternManifest,
    CustomPatternManifestEntry,
)


class CustomPatternManifestError(ValueError):
    """Raised when a custom-pattern manifest file is malformed."""


class LoadCustomPatterns:
    """Reads a JSON manifest into a typed CustomPatternManifest."""

    def load(self, path: Path) -> CustomPatternManifest:
        """Parse the JSON at ``path`` into a CustomPatternManifest.

        Expected shape::
            {
              "patterns": [
                {"name": "EventSourcedAggregate",
                 "icp_spec_name": "python/custom/EventSourcedAggregateICP"}
              ],
              "extra_spec_roots": ["./my_specs/"]
            }
        """
        if not path.is_file():
            raise CustomPatternManifestError(f"manifest not found: {path}")
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise CustomPatternManifestError(
                f"invalid JSON in {path}: {exc}"
            ) from exc
        return self._parse(data, path)

    def _parse(self, data: object, path: Path) -> CustomPatternManifest:
        if not isinstance(data, dict):
            raise CustomPatternManifestError(
                f"{path}: top-level must be a JSON object"
            )
        raw_patterns = data.get("patterns", [])
        if not isinstance(raw_patterns, list):
            raise CustomPatternManifestError(
                f"{path}: 'patterns' must be a list"
            )
        entries: list[CustomPatternManifestEntry] = []
        for i, raw in enumerate(raw_patterns):
            if not isinstance(raw, dict):
                raise CustomPatternManifestError(
                    f"{path}: patterns[{i}] must be an object"
                )
            entries.append(CustomPatternManifestEntry(
                name=str(raw.get("name", "")),
                icp_spec_name=str(raw.get("icp_spec_name", "")),
            ))
        roots = tuple(str(r) for r in data.get("extra_spec_roots", []))
        return CustomPatternManifest(
            entries=tuple(entries), extra_spec_roots=roots,
        )
