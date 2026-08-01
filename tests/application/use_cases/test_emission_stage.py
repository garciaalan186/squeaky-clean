"""Tests for EmissionStage: ICP fan-out, merged impl, resume checkpoint."""

import dataclasses
import json
from pathlib import Path

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.emission_stage import EmissionStage
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.architecture_merger import ArchitectureMerger
from squeaky_clean.application.generation.architecture.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)
from tests.application.use_cases.run_eval_stub_deps import _impl, build_stub_deps


def _ctx(tmp_path: Path, arch: ArchitectureSpec) -> PipelineContext:
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    ctx = PipelineContext(
        problem=P0, output_dir=out,
        emitter=CheckpointEmitter("P0", out),
        lifecycle=LifecycleTimestampLog(out),
    )
    return dataclasses.replace(ctx, arch=arch)


def test_stub_orchestrator_sets_module_impls_and_merged_impl(tmp_path: Path) -> None:
    deps = build_stub_deps()
    arch = ArchitectureSpec(modules=(_impl().module,),
                            graph=ArchitectureGraph(edges={}))
    stage = EmissionStage(
        OrchestrateArchitecture(deps.orchestrate_module), ArchitectureMerger())
    out = stage.run(_ctx(tmp_path, arch))
    expected = _impl()
    assert len(out.module_impls) == 1
    assert out.module_impls[0].implemented_classes == expected.implemented_classes
    assert out.impl is not None
    assert out.impl.implemented_classes == expected.implemented_classes
    assert out.impl.total_cost_usd == expected.total_cost_usd


def test_emitter_checkpoint_written_at_icps_done(tmp_path: Path) -> None:
    deps = build_stub_deps()
    arch = ArchitectureSpec(modules=(_impl().module,),
                            graph=ArchitectureGraph(edges={}))
    ctx = _ctx(tmp_path, arch)
    EmissionStage(
        OrchestrateArchitecture(deps.orchestrate_module), ArchitectureMerger(),
    ).run(ctx)
    checkpoint = json.loads((ctx.output_dir / "CHECKPOINT.json").read_text())
    assert checkpoint["stage"] == "icps_done"
    assert (ctx.output_dir / "_resume_module_impls.json").exists()
