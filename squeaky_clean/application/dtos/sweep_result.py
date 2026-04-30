"""SweepResult DTO: aggregated outcome of one parallel sweep."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle


@dataclass(frozen=True)
class SweepResult:
    """Frozen sweep-level result with shared run dir + per-problem bundles."""

    run_dir: Path
    bundles: tuple[EvalReportBundle, ...]
    total_cost_usd: float
    total_duration_ms: int
