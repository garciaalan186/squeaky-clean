"""GitInfoAdapter: subprocess-backed GitInfo port implementation."""

from __future__ import annotations

import subprocess

from squeaky_clean.domain.interfaces.provenance.git_info import GitInfo

_TIMEOUT_SECONDS = 5


class GitInfoAdapter(GitInfo):
    """Reads the framework checkout's HEAD SHA via ``git rev-parse``.

    Extracted from ``RunManifest._git_sha`` (R6.4c) so the application
    layer stays subprocess-free. Best-effort: any failure (git absent,
    not a checkout, timeout) degrades to ``"unknown"`` — manifest loss
    of provenance must never break a run.
    """

    def head_sha(self) -> str:
        """Return the current HEAD commit SHA, or ``"unknown"``."""
        try:
            out = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
            return out.stdout.strip() if out.returncode == 0 else "unknown"
        except (OSError, subprocess.TimeoutExpired):
            return "unknown"
