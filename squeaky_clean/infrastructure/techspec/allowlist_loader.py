"""allowlist_loader: load per-(category,tech) allowed_doc_origins from disk."""

import json
from pathlib import Path
from typing import cast

from squeaky_clean.infrastructure.techspec.composite_techspec_resolver_helpers import (
    AllowlistRegistry,
)


def load_allowlist_registry(root: Path) -> AllowlistRegistry:
    """Walk eval/tech_specs/, harvest allowed_doc_origins per (cat, tech)."""
    registry: dict[tuple[str, str], tuple[str, ...]] = {}
    if not root.is_dir():
        return registry
    for json_file in root.rglob("*.json"):
        if json_file.name.startswith("_"):
            continue
        rel = json_file.relative_to(root).parts
        if len(rel) < 3 or rel[0] == ".cache":
            continue
        category, technology = rel[0], rel[1]
        try:
            data = cast(dict[str, object], json.loads(json_file.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
        origins = data.get("allowed_doc_origins")
        if not isinstance(origins, list):
            continue
        prefixes = tuple(str(o) for o in cast(list[object], origins))
        if prefixes:
            registry[(category, technology)] = prefixes
    return registry
