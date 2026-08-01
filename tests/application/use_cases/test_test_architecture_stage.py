"""Tests for TestArchitectureStage: per-module oracles, filtering, security."""

import dataclasses
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import CheckpointEmitter
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.evaluation.eval.run.stages.test_architecture_stage import (
    TestArchitectureStage,
)
from squeaky_clean.application.generation.architecture.architecture_merger import ArchitectureMerger
from squeaky_clean.application.shared.config.run_config import RunConfig
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


def _arch(module: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(modules=(module,), graph=ArchitectureGraph(edges={}))


def _calculator_module() -> ModuleSpec:
    cls = ClassSpec(
        name="Calculator", pattern="SimpleClass", implements=None,
        methods=("add(a: int): int", "subtract(a: int): int",
                 "multiply(a: int): int", "divide(a: int): int"),
        depends=(), concretes=())
    return ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(cls,), invariants=())


def _infra_module() -> ModuleSpec:
    cls = ClassSpec(name="RedisAdapter", pattern="Adapter", implements=None,
                    methods=("add(k: str): void",), depends=(), concretes=())
    return ModuleSpec(name="Cache", layer=LayerType.INFRASTRUCTURE, exports=(),
                      depends=(), classes=(cls,), invariants=())


def test_module_owning_criterion_verbs_gets_an_oracle_call(tmp_path: Path) -> None:
    deps = build_stub_deps()
    out = TestArchitectureStage(deps, ArchitectureMerger()).run(
        _ctx(tmp_path, _arch(_calculator_module())))
    assert cast(Mock, deps.generate_test_architecture).execute.call_count == 1
    assert out.counters.test_criteria_filtered == 0
    assert out.test_arch is not None


def test_value_object_only_module_is_fully_filtered(tmp_path: Path) -> None:
    deps = build_stub_deps()
    arch = _arch(_impl().module)  # single Domain module, ValueObject only
    out = TestArchitectureStage(deps, ArchitectureMerger()).run(_ctx(tmp_path, arch))
    cast(Mock, deps.generate_test_architecture).execute.assert_not_called()
    assert out.counters.test_criteria_filtered == len(P0.acceptance_criteria)
    assert out.test_arch is not None
    assert out.test_arch.test_skeletons == ()


def test_infrastructure_layer_modules_are_skipped(tmp_path: Path) -> None:
    deps = build_stub_deps()
    out = TestArchitectureStage(deps, ArchitectureMerger()).run(
        _ctx(tmp_path, _arch(_infra_module())))
    cast(Mock, deps.generate_test_architecture).execute.assert_not_called()
    assert out.counters.test_criteria_filtered == 0


def test_sec_arch_empty_when_security_tests_disabled(tmp_path: Path) -> None:
    deps = build_stub_deps()  # enable_security_tests defaults to False
    out = TestArchitectureStage(deps, ArchitectureMerger()).run(
        _ctx(tmp_path, _arch(_calculator_module())))
    cast(Mock, deps.review_security).execute.assert_not_called()
    assert out.sec_arch is not None
    assert out.sec_arch.gherkin_scenarios == ()
    assert out.sec_arch.test_skeletons == ()


def test_security_generation_runs_per_module_when_enabled(tmp_path: Path) -> None:
    deps = dataclasses.replace(
        build_stub_deps(), run_config=RunConfig(enable_security_tests=True))
    TestArchitectureStage(deps, ArchitectureMerger()).run(
        _ctx(tmp_path, _arch(_calculator_module())))
    assert cast(Mock, deps.review_security).execute.call_count == 1
    assert cast(Mock, deps.generate_security_tests).execute.call_count == 1
