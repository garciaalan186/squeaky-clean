"""ReplicateSummaryWriter: persist a ReplicateSummary as JSON + Markdown."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.evaluation.eval.sweep.replicate_report import (
    ReplicateReport,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import (
    ReplicateSummary,
)
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text

# R5.1 policy: headline claims (fix accepted, regression declared, baseline
# updates) require N >= 3 replicates; below that a run is exploratory.
CLAIMS_MIN_REPLICATES: int = 3


class ReplicateSummaryWriter:
    """Writes replicate_summary.json + replicate_summary.md into a run dir."""

    def write(self, out_dir: Path, report: ReplicateReport) -> Path:
        """Persist ``report``; return the JSON path."""
        payload = asdict(report.summary)
        payload["reports"] = list(report.report_paths)
        json_path = out_dir / "replicate_summary.json"
        atomic_write_text(json_path, json.dumps(payload, indent=2))
        atomic_write_text(
            out_dir / "replicate_summary.md",
            "\n".join(self._md(report.summary)),
        )
        return json_path

    @staticmethod
    def _md(s: ReplicateSummary) -> list[str]:
        lines = [
            f"# Replicate Summary — {s.problem_id} (N={s.replicates})", "",
            "| metric | mean | σ |",
            "|---|---:|---:|",
            f"| tests_pass | {s.tests_pass_mean:.2f} | {s.tests_pass_stddev:.2f} |",
            f"| functional | {s.functional_pass_mean:.2f} "
            f"| {s.functional_pass_stddev:.2f} |",
            f"| security | {s.security_pass_mean:.2f} "
            f"| {s.security_pass_stddev:.2f} |",
            f"| cost USD | {s.cost_usd_mean:.4f} | {s.cost_usd_stddev:.4f} |",
            f"| wall-clock ms | {s.wall_clock_ms_mean:.0f} "
            f"| {s.wall_clock_ms_stddev:.0f} |",
            "",
            f"- cache hit ratio: {s.cache_hit_ratio:.2f}",
        ]
        if s.replicates < CLAIMS_MIN_REPLICATES:
            lines.append(
                f"- **N={s.replicates} is below the claims threshold "
                f"(N>={CLAIMS_MIN_REPLICATES})** — treat as exploratory."
            )
        return lines
