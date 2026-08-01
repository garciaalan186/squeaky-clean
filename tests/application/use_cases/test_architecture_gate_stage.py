"""Tests for ArchitectureGateStage: cross-module and convention hard gates."""

import dataclasses
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.architecture_gate_stage import (
    ArchitectureGateStage,
)
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.cross_module_dependency_error import (
    CrossModuleDependencyError,
)
from squeaky_clean.application.generation.validation.contract_registry import ContractRegistry
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
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


def _stage(tmp_path: Path) -> ArchitectureGateStage:
    contracts = ContractRegistry(root=tmp_path / "contracts")
    return ArchitectureGateStage(build_stub_deps(), contracts)


def _violating_arch() -> ArchitectureSpec:
    """A class depending on an unknown module -> cross-module violation."""
    cls = ClassSpec(name="Svc", pattern="SimpleClass", implements=None,
                    methods=("run(x: int): int",), depends=("Ghost::Thing",),
                    concretes=())
    module = ModuleSpec(name="Calc", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(cls,), invariants=())
    return ArchitectureSpec(modules=(module,), graph=ArchitectureGraph(edges={}))


def test_clean_arch_passes_through_unchanged(tmp_path: Path) -> None:
    arch = ArchitectureSpec(
        modules=(_impl().module,), graph=ArchitectureGraph(edges={}),
    )
    ctx = _ctx(tmp_path, arch)
    out = _stage(tmp_path).run(ctx)
    assert out.arch is arch
    assert out.counters.http_violations == 0
    assert out.counters.architect_retries == 0
    assert not (ctx.output_dir / "CROSS_MODULE_VIOLATIONS.txt").exists()


def test_cross_module_violation_raises_and_writes_artifact(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, _violating_arch())
    with pytest.raises(CrossModuleDependencyError) as excinfo:
        _stage(tmp_path).run(ctx)
    assert excinfo.value.violations
    artifact = ctx.output_dir / "CROSS_MODULE_VIOLATIONS.txt"
    assert artifact.exists()
    assert "unknown module 'Ghost'" in artifact.read_text()
