"""ResumeRun: pick up a partial pipeline run from a CHECKPOINT.json (G3)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.resume.checkpoint_checksum import CheckpointChecksum
from squeaky_clean.application.evaluation.eval.resume.checkpoint_reader import CheckpointReader
from squeaky_clean.application.evaluation.eval.resume.completed_metrics_reader import (
    CompletedMetricsReader,
)
from squeaky_clean.application.evaluation.eval.resume.resume_run_executor import ResumeRunExecutor
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class ResumeRun:
    """Top-level resume entry point: read checkpoint, dispatch executor."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._logger: RunLogger = logger or NullRunLogger()
        self._reader: CheckpointReader = CheckpointReader(self._logger)
        self._checksum: CheckpointChecksum = CheckpointChecksum()

    def resume(
        self, run_dir: Path, problem: ProblemSpec, deps: RunEvalDependencies,
    ) -> EvalReportBundle:
        """Resume the pipeline at the checkpointed stage; restart on mismatch."""
        expected = self._checksum.compute(problem.id)
        cp = self._reader.read(run_dir, expected_checksum=expected)
        if cp is None:
            self._logger.event(
                "resume_restart", run_dir=str(run_dir),
                reason="missing_or_mismatched_checkpoint",
            )
            return ResumeRunExecutor(deps).run_full(problem, run_dir)
        if cp.stage == "complete":
            return self._short_circuit(cp, problem, run_dir)
        try:
            return ResumeRunExecutor(deps).resume_from(cp, problem, run_dir)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self._logger.event(
                "resume_deserialize_failed", run_dir=str(run_dir),
                stage=cp.stage, error=str(exc),
            )
            return ResumeRunExecutor(deps).run_full(problem, run_dir)

    def _short_circuit(
        self, cp: RunCheckpoint, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        metrics: EvalMetrics = CompletedMetricsReader().read(
            self._find_report(run_dir), cp.cost_spent_usd,
        )
        return EvalReportBundle(
            problem=problem, metrics=metrics,
            test_run_result=TestRunResult(
                passed=0, failed=0, errors=0, duration_ms=0,
                raw_output="resumed: stage=complete, prior bundle reused",
            ),
            validation=ValidationReport(violations=(), files_scanned=0),
        )

    def _find_report(self, run_dir: Path) -> Path | None:
        for child in run_dir.iterdir():
            cand = child / "eval_report.json"
            if cand.exists():
                return cand
        return None
