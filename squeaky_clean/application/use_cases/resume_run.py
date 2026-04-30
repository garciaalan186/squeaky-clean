"""ResumeRun: pick up a partial pipeline run from a CHECKPOINT.json (G3)."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.checkpoint_checksum import CheckpointChecksum
from squeaky_clean.application.use_cases.checkpoint_reader import CheckpointReader
from squeaky_clean.application.use_cases.resume_run_executor import ResumeRunExecutor
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger


class ResumeRun:
    """Top-level resume entry point: read checkpoint, dispatch executor."""

    def __init__(self) -> None:
        self._reader: CheckpointReader = CheckpointReader()
        self._checksum: CheckpointChecksum = CheckpointChecksum()
        self._logger: JSONLogger = JSONLogger()

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
        report_path = self._find_report(run_dir)
        metrics = EvalMetrics.empty()
        metrics.estimated_cost_usd = cp.cost_spent_usd
        if report_path is not None:
            data = json.loads(report_path.read_text()).get("metrics", {})
            metrics.estimated_cost_usd = float(
                data.get("estimated_cost_usd", cp.cost_spent_usd)
            )
            metrics.tests_pass = float(data.get("tests_pass", 0.0))
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
