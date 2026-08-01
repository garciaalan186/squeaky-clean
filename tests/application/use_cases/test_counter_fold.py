"""Tests for CounterFold (stage counters folded into frozen EvalMetrics)."""

import dataclasses
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.counter_fold import CounterFold
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.stage_counters import StageCounters
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl


def _ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(
        ctx, impl=_impl(), module_impls=(_impl(),), compile_errors=3,
        counters=StageCounters(
            di_violations=1, architect_retries=2, http_violations=4,
            notation_novelty=5, test_criteria_filtered=6,
            infra_explicit=1, infra_derived=2, mcda_runs=2,
            dep_install_failed=True,
        ),
    )


def test_apply_folds_counters_into_notation_and_reliability(
    tmp_path: Path,
) -> None:
    metrics = CounterFold().apply(_ctx(tmp_path), EvalMetrics.empty())
    assert metrics.notation.dependency_injection_violations == 1
    assert metrics.notation.http_convention_violations == 4
    assert metrics.notation.notation_novelty == 5
    assert metrics.notation.test_criteria_filtered == 6
    assert metrics.notation.dependency_install_failed is True
    assert metrics.reliability.architect_retries == 2
    assert metrics.reliability.compile_errors == 3


def test_apply_returns_new_metrics_and_keeps_input_frozen(
    tmp_path: Path,
) -> None:
    base = EvalMetrics.empty()
    out = CounterFold().apply(_ctx(tmp_path), base)
    assert out is not base
    assert base.reliability.compile_errors == 0
