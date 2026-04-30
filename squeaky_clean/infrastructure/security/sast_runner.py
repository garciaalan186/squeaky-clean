"""SASTRunner: invoke bandit/semgrep on a generated project tree."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SASTResult:
    """One SAST run summary."""

    tool: str
    available: bool
    issues: int
    raw_output: str


class SASTRunner:
    """Runs bandit (Python) or semgrep (any) over a generated project."""

    def run_bandit(self, project_dir: Path) -> SASTResult:
        """Run `bandit -r <project_dir>/src` if installed, else mark unavailable."""
        if shutil.which("bandit") is None:
            return SASTResult("bandit", False, 0, "")
        target = project_dir / "src"
        if not target.exists():
            return SASTResult("bandit", True, 0, "no src/ to scan")
        out = subprocess.run(
            ["bandit", "-q", "-r", str(target)],
            capture_output=True, text=True, timeout=60, check=False,
        )
        issues = sum(1 for line in out.stdout.splitlines() if line.startswith(">>"))
        return SASTResult("bandit", True, issues, out.stdout[:8000])

    def run_semgrep(self, project_dir: Path) -> SASTResult:
        """Run `semgrep --config=auto` if installed, else mark unavailable."""
        if shutil.which("semgrep") is None:
            return SASTResult("semgrep", False, 0, "")
        out = subprocess.run(
            ["semgrep", "--config", "auto", "--quiet", str(project_dir)],
            capture_output=True, text=True, timeout=120, check=False,
        )
        issues = sum(1 for line in out.stdout.splitlines() if "issue" in line.lower())
        return SASTResult("semgrep", True, issues, out.stdout[:8000])
