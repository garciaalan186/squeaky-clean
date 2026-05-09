"""CheckpointChecksum: compute a stable hash of (problem_id + spec_lib_version)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from squeaky_clean.application.use_cases.spec_version_stamp import SpecVersionStamp

_DEFAULT_SPECS_ROOT = (
    Path(__file__).resolve().parents[3] / "squeaky_clean" / "interface" / "agent_specs"
)


class CheckpointChecksum:
    """Compute a SHA256 of ``problem_id + spec_library_version`` for safety."""

    def __init__(self, specs_root: Path | None = None) -> None:
        self._stamp: SpecVersionStamp = SpecVersionStamp(
            specs_root or _DEFAULT_SPECS_ROOT,
        )

    def compute(self, problem_id: str) -> str:
        """Return hex-encoded SHA256 of (problem_id + '@' + spec_version)."""
        version = self._stamp.version()
        material = f"{problem_id}@{version}".encode()
        return hashlib.sha256(material).hexdigest()
