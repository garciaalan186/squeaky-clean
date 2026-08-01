"""RunManifest: write a reproducibility manifest.json for one meta-eval run."""

from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from squeaky_clean.application.generation.emission.spec_version_stamp import SpecVersionStamp
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.domain.interfaces.provenance.git_info import GitInfo
from squeaky_clean.domain.interfaces.provenance.toolchain_info import ToolchainInfo

_FRAMEWORK_ROOT = Path(__file__).resolve().parents[5]
_DEFAULT_SPEC_DIRS: tuple[Path, ...] = (
    _FRAMEWORK_ROOT / "squeaky_clean" / "interface" / "agent_specs",
)


class RunManifest:
    """Captures model IDs, spec hashes, framework SHA, replicate seeds.

    Provenance probes (git SHA, toolchains) arrive via the ``GitInfo`` /
    ``ToolchainInfo`` ports (R6.4c); unwired they degrade to unknown/{}.
    ``spec_dirs``/``replicate_id`` are per-manifest configuration and
    default to the framework spec library / replicate 0."""

    def __init__(
        self, git_info: GitInfo | None = None,
        toolchain_info: ToolchainInfo | None = None,
        *, spec_dirs: Sequence[Path] = _DEFAULT_SPEC_DIRS, replicate_id: int = 0,
    ) -> None:
        self._git: GitInfo | None = git_info
        self._toolchains: ToolchainInfo | None = toolchain_info
        self._spec_dirs: Sequence[Path] = spec_dirs
        self._replicate_id: int = replicate_id

    def write(self, run_dir: Path, models: dict[str, str]) -> Path:
        """Write run_dir/manifest.json and return its path."""
        spec_dirs = self._spec_dirs
        manifest = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "models": dict(models),
            "replicate_id": self._replicate_id,
            "framework_sha": self._git.head_sha() if self._git else "unknown",
            "toolchains": self._toolchains.versions() if self._toolchains else {},
            "spec_library_version": self._stamp(spec_dirs),
            "spec_hashes": self._hash_spec_dirs(spec_dirs),
        }
        target = run_dir / "manifest.json"
        atomic_write_text(
            target, json.dumps(manifest, indent=2, sort_keys=True),
        )
        return target

    def _stamp(self, spec_dirs: Sequence[Path]) -> str:
        for d in spec_dirs:
            stamp = SpecVersionStamp(d).version()
            if "unversioned" not in stamp:
                return stamp
        return "0.0.0+unversioned"

    def _hash_spec_dirs(self, dirs: Sequence[Path]) -> dict[str, str]:
        out: dict[str, str] = {}
        for root in dirs:
            if not root.exists():
                continue
            for p in sorted(root.rglob("*.md")):
                try:
                    rel = str(p.relative_to(root))
                except ValueError:
                    rel = p.name
                out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        return out
