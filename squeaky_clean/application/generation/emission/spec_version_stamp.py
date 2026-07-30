"""SpecVersionStamp: read VERSION file under agent_specs to label spec releases."""

from __future__ import annotations

from pathlib import Path

_DEFAULT_VERSION = "0.0.0+unversioned"


class SpecVersionStamp:
    """Read the agent-spec library version from a VERSION file."""

    def __init__(self, specs_root: Path) -> None:
        self._specs_root: Path = specs_root

    def version(self) -> str:
        """Return the library's stamped version, or the default sentinel."""
        version_file = self._specs_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip() or _DEFAULT_VERSION
        return _DEFAULT_VERSION
