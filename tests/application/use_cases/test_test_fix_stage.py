"""Tests for TestFixStage: test run capture, repair no-ops, lifecycle record."""

import dataclasses
import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import (
    RunEvalDependencies,
)
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.test_fix_stage import TestFixStage
from squeaky_clean.application.generation.repair.compile_gate import CompileGate
from squeaky_clean.application.generation.repair.fixer_stage import (
    FixerStage,
    FixerStageResult,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def _primed_ctx(tmp_path: Path) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    impl = _impl()
    arch = ArchitectureSpec(modules=(impl.module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(
        ctx, arch=arch, impl=impl,
        fix_stats=FixerStageResult(0, 0, 0, 0.0, 0, 0))


def _stage(deps: RunEvalDependencies) -> TestFixStage:
    fixer = FixerStage(None, None)
    return TestFixStage(deps, fixer, CompileGate(None, fixer, None))


def _last_lifecycle_entry(ctx: PipelineContext) -> dict[str, object]:
    lines = (ctx.output_dir / "squib_lifecycle.jsonl").read_text().splitlines()
    entry: dict[str, object] = json.loads(lines[-1])
    return entry


def test_failing_run_is_captured_with_no_repairers_wired(tmp_path: Path) -> None:
    deps = build_stub_deps()  # stub runner: 2 passed, 1 failed
    ctx = _primed_ctx(tmp_path)
    out = _stage(deps).run(ctx)
    assert out.test_run is not None
    assert (out.test_run.passed, out.test_run.failed) == (2, 1)
    assert out.func_run is None  # no functional runner wired
    assert out.fix_stats == FixerStageResult(0, 0, 0, 0.0, 0, 0)
    # Fixer/repairers are unwired no-ops: the runner is invoked exactly once.
    assert cast(Mock, deps.test_runner).run.call_count == 1
    entry = _last_lifecycle_entry(ctx)
    assert entry["event"] == "tests_complete"
    assert entry["all_passed"] is False
    assert entry["failed"] == 1
    checkpoint = json.loads((ctx.output_dir / "CHECKPOINT.json").read_text())
    assert checkpoint["stage"] == "fixed"


def test_green_run_records_all_passed(tmp_path: Path) -> None:
    deps = build_stub_deps()
    cast(Mock, deps.test_runner).run.return_value = TestRunResult(
        passed=3, failed=0, errors=0, duration_ms=10, raw_output="3 passed")
    ctx = _primed_ctx(tmp_path)
    out = _stage(deps).run(ctx)
    assert out.test_run is not None
    assert out.test_run.failed == 0
    entry = _last_lifecycle_entry(ctx)
    assert entry["all_passed"] is True
    assert entry["passed"] == 3
