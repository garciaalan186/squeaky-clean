"""ResumeHelper: utilities for resuming a partially-completed meta-eval run.

Resumption strategy: the CachingLLMGateway content-addresses every LLM
response by (model, prompts, temperature, replicate_id). Re-running the
same problem set against the populated cache replays all completed
agent calls instantly with $0 cost; only the in-flight or post-cache
work needs to re-execute. ResumeHelper inspects a run dir and reports
which problems already finished, so the CLI can skip them.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path


class ResumeHelper:
    """Inspect a meta-eval run dir and report completed problem ids."""

    def completed_problem_ids(
        self, run_dir: Path,
    ) -> Sequence[str]:
        """Return ids of problems whose `eval_report.json` exists in run_dir."""
        if not run_dir.exists():
            return ()
        out: list[str] = []
        for child in sorted(run_dir.iterdir()):
            if not child.is_dir():
                continue
            if (child / "eval_report.json").exists():
                out.append(self._extract_id(child.name))
        return tuple(out)

    def _extract_id(self, dir_name: str) -> str:
        """Pull the leading P0/P1/... token out of a per-problem dir name."""
        parts = dir_name.split("-")
        for p in parts:
            if p.startswith("P") and any(c.isdigit() for c in p):
                return p
        return dir_name
