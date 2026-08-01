"""Tests for RegressionGate (R5.2)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome
from squeaky_clean.application.evaluation.eval.report.regression_gate import (
    RegressionGate,
)
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import (
    EvalReportBundle,
)
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.generation.validation.validation_report import (
    ValidationReport,
)
from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult

_MODELS = {"architect": "sonnet", "manager": "sonnet",
           "icp": "haiku", "fixer": "sonnet"}
_ROUTING = tuple(sorted(f"{t}={m}" for t, m in _MODELS.items()))


def _golden() -> GoldenMetrics:
    return GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.05,
        functional_pass_mean=1.0, functional_pass_stddev=0.05,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.05, cost_usd_stddev=0.01,
        model_routing=_ROUTING, calibrated_run="meta-evaluation_454",
    )


def _result(tests_pass: float, golden: GoldenMetrics | None) -> SweepResult:
    problem = ProblemSpec(
        id="P2", slug="p2", description="x", tier=2,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], golden_metrics=golden,
    )
    bundle = EvalReportBundle(
        problem=problem,
        metrics=EvalMetrics(test_outcome=TestOutcome(
            tests_pass=tests_pass, functional_tests_pass=tests_pass,
        )),
        test_run_result=TestRunResult(
            passed=1, failed=0, errors=0, duration_ms=1, raw_output="",
        ),
        validation=ValidationReport(violations=(), files_scanned=1),
    )
    return SweepResult(
        run_dir=Path("/tmp/x"), bundles=(bundle,),
        total_cost_usd=0.05, total_duration_ms=1,
    )


def test_uncalibrated_problem_never_gates() -> None:
    a = RegressionGate().assess(_result(0.0, None), _MODELS)
    assert a.verdicts == ("P2: no golden (uncalibrated)",)
    assert not a.has_regressions


def test_routing_mismatch_is_not_comparable() -> None:
    a = RegressionGate().assess(
        _result(0.0, _golden()), {**_MODELS, "architect": "opus"},
    )
    assert "not comparable" in a.verdicts[0]
    assert not a.has_regressions


def test_matching_score_passes_gate() -> None:
    a = RegressionGate().assess(_result(1.0, _golden()), _MODELS)
    assert a.verdicts[0].startswith("P2: OK")
    assert not a.has_regressions


def test_two_sigma_drop_trips_gate() -> None:
    # golden 1.00 ± 0.05; current 0.10 → drop of 18σ >= 2σ threshold.
    a = RegressionGate().assess(_result(0.1, _golden()), _MODELS)
    assert "REGRESSION" in a.verdicts[0]
    assert a.has_regressions
    assert a.records[0].metric == "tests_pass"
    assert a.records[0].sigma_drop >= 2.0


