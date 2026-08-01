"""Tests for IntegrationStage: project-tree write + integrated checkpoint."""

import dataclasses
import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.integration_stage import IntegrationStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
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
    empty = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(
        ctx, arch=arch, impl=impl, test_arch=empty, sec_arch=empty)


def test_delegates_to_integrate_module_with_stage_outputs(tmp_path: Path) -> None:
    deps = build_stub_deps()
    ctx = _primed_ctx(tmp_path)
    out = IntegrationStage(deps).run(ctx)
    assert out is ctx  # stage adds no new context slots
    integrate = cast(Mock, deps.integrate_module)
    integrate.execute.assert_called_once()
    request = integrate.execute.call_args.args[0]
    assert request.implementation is ctx.impl
    assert request.test_architecture is ctx.test_arch
    assert request.security_test_architecture is ctx.sec_arch
    assert request.output_dir == ctx.output_dir


def test_marks_checkpoint_integrated_and_skips_auto_extras(tmp_path: Path) -> None:
    deps = build_stub_deps()  # infrastructure_mode defaults to "manual"
    ctx = _primed_ctx(tmp_path)
    IntegrationStage(deps).run(ctx)
    checkpoint = json.loads((ctx.output_dir / "CHECKPOINT.json").read_text())
    assert checkpoint["stage"] == "integrated"
    assert checkpoint["integration_done"] is True
    # Manual mode: no wiring module and no dependency manifests are emitted.
    assert not (ctx.output_dir / "requirements.txt").exists()
    assert list(ctx.output_dir.glob("**/wiring*")) == []
