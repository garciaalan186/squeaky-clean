"""Tests for ReplicateRunner (R5.1 statistics wiring)."""

import dataclasses
import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome
from squeaky_clean.application.evaluation.eval.run.eval_result_dto import EvalResult
from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder
from squeaky_clean.interface.cli.invocations.infra_settings import InfraSettings
from squeaky_clean.interface.cli.invocations.run_settings import RunSettings
from squeaky_clean.interface.cli.replicates.replicate_runner import ReplicateRunner
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


def make_problem_spec() -> ProblemSpec:
    return ProblemSpec(
        id="P0", slug="p0", description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )


def _runner() -> ReplicateRunner:
    return ReplicateRunner(DependencyBuilder(), RunConfigFactory())


def _result(run_dir: Path, tests_pass: float, cost: float) -> EvalResult:
    report = run_dir / "problem-set-0-x-code" / "eval_report.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    return EvalResult(
        problem_id="P0",
        metrics=EvalMetrics(
            test_outcome=TestOutcome(
                tests_pass=tests_pass, functional_tests_pass=tests_pass,
            ),
            cost=CostBreakdown(estimated_cost_usd=cost),
            total_wall_clock_ms=1000,
        ),
        report_path=report,
    )


def test_with_seed_preserves_every_flag() -> None:
    # Rebuilding settings field-by-field silently dropped cost caps and
    # security flags on replicate runs; replace() must keep them all.
    settings = RunSettings(
        budget=CostBudget(max_cost_usd=5.0),
        enable_security_tests=True, enable_sast=True,
        retry=RetryPolicy(max_fixer_passes=2),
        infra=InfraSettings(infrastructure_mode="auto"),
    )
    seeded = ReplicateRunner._with_seed(settings, 2)
    assert seeded.seed == 2
    for f in dataclasses.fields(RunSettings):
        if f.name == "seed":
            continue
        assert getattr(seeded, f.name) == getattr(settings, f.name), f.name


def test_write_summary_aggregates_all_metrics(tmp_path: Path) -> None:
    results = [
        _result(tmp_path, 1.0, 0.05),
        _result(tmp_path, 0.5, 0.07),
        _result(tmp_path, 1.0, 0.06),
    ]
    outcome = _runner()._write_summary(make_problem_spec(), results)
    assert outcome.runs == 3
    # The summary must land INSIDE the first replicate's run dir.
    assert outcome.summary_path.parent == tmp_path
    payload = json.loads(outcome.summary_path.read_text())
    assert payload["replicates"] == 3
    assert abs(payload["tests_pass_mean"] - (2.5 / 3)) < 1e-9
    assert payload["tests_pass_stddev"] > 0.0
    assert abs(payload["cost_usd_mean"] - 0.06) < 1e-9
    assert payload["wall_clock_ms_mean"] == 1000.0
    assert len(payload["reports"]) == 3
    md = (outcome.summary_path.parent / "replicate_summary.md").read_text()
    assert "N=3" in md
    assert "exploratory" not in md  # at the claims threshold


def test_below_threshold_run_is_labeled_exploratory(tmp_path: Path) -> None:
    outcome = _runner()._write_summary(
        make_problem_spec(), [_result(tmp_path, 1.0, 0.05)],
    )
    md = (outcome.summary_path.parent / "replicate_summary.md").read_text()
    assert "below the claims threshold" in md
    assert "exploratory" in md
