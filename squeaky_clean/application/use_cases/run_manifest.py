"""RunManifest: write a reproducibility manifest.json for one meta-eval run."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from squeaky_clean.application.use_cases.spec_version_stamp import SpecVersionStamp


class RunManifest:
    """Captures model IDs, spec hashes, framework SHA, replicate seeds."""

    def write(
        self,
        run_dir: Path,
        models: dict[str, str],
        spec_dirs: Sequence[Path],
        replicate_id: int,
    ) -> Path:
        """Write run_dir/manifest.json and return its path."""
        manifest = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "models": dict(models),
            "replicate_id": replicate_id,
            "framework_sha": self._git_sha(),
            "spec_library_version": self._stamp(spec_dirs),
            "spec_hashes": self._hash_spec_dirs(spec_dirs),
        }
        target = run_dir / "manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(manifest, indent=2, sort_keys=True))
        return target

    def _stamp(self, spec_dirs: Sequence[Path]) -> str:
        for d in spec_dirs:
            stamp = SpecVersionStamp(d).version()
            if "unversioned" not in stamp:
                return stamp
        return "0.0.0+unversioned"

    def _git_sha(self) -> str:
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            return out.stdout.strip() if out.returncode == 0 else "unknown"
        except (OSError, subprocess.TimeoutExpired):
            return "unknown"

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
