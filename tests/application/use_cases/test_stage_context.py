"""Tests for PipelineContext: the frozen state threaded between stages (R6.2)."""

import dataclasses
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.stage_counters import StageCounters
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)


def _ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    return PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )


def test_defaults_cover_every_stage_result_slot(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    assert ctx.counters == StageCounters()
    assert ctx.arch is None
    assert ctx.test_arch is None
    assert ctx.sec_arch is None
    assert ctx.tech_specs == {}
    assert ctx.module_impls == ()
    assert ctx.impl is None
    assert ctx.validation is None
    assert ctx.compile_errors == 0
    assert ctx.test_run is None
    assert ctx.func_run is None
    assert ctx.fix_stats is None


def test_is_frozen(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.compile_errors = 5  # type: ignore[misc]


def test_replace_threads_new_results_and_keeps_run_inputs(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    updated = dataclasses.replace(
        ctx, compile_errors=2,
        counters=dataclasses.replace(ctx.counters, architect_retries=1),
    )
    assert updated is not ctx
    assert updated.compile_errors == 2
    assert updated.counters.architect_retries == 1
    assert ctx.compile_errors == 0
    assert updated.problem is ctx.problem
    assert updated.output_dir == ctx.output_dir
    assert updated.emitter is ctx.emitter
    assert updated.lifecycle is ctx.lifecycle
