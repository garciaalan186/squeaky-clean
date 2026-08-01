"""ToolchainProbeAdapter: subprocess-backed ToolchainInfo port implementation."""

from __future__ import annotations

import re
import subprocess

from squeaky_clean.domain.interfaces.provenance.toolchain_info import ToolchainInfo

_TIMEOUT_SECONDS = 5
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
# tool -> version argv. Scores depend on these (Node 22 broke the runner;
# javac 11 rejects records CI's JDK 21 accepts) — R5.9: a manifest without
# toolchain versions cannot attribute a score to an environment.
_TOOLS: dict[str, list[str]] = {
    "node": ["node", "--version"],
    "npm": ["npm", "--version"],
    "javac": ["javac", "--version"],
    "mvn": ["mvn", "--version"],
    "go": ["go", "version"],
    "cargo": ["cargo", "--version"],
}


class ToolchainProbeAdapter(ToolchainInfo):
    """Probes local toolchain versions (moved from toolchain_probe, R6.4c)."""

    def versions(self) -> dict[str, str]:
        """First version line per tool; ``"absent"`` when not on PATH."""
        return {name: _first_line(argv) for name, argv in _TOOLS.items()}


def _first_line(argv: list[str]) -> str:
    try:
        completed = subprocess.run(
            argv, capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "absent"
    text = _ANSI.sub("", completed.stdout or completed.stderr).strip()
    return text.splitlines()[0].strip() if text else "absent"
