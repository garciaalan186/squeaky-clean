"""ReplicateReport DTO: a ReplicateSummary plus its per-replicate reports."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import (
    ReplicateSummary,
)


@dataclass(frozen=True)
class ReplicateReport:
    """What ReplicateSummaryWriter persists for one replicated problem."""

    summary: ReplicateSummary
    report_paths: tuple[str, ...] = ()
    # Failed replicates (isolated, not aborting): "replicate N: Error..."
    failures: tuple[str, ...] = ()
