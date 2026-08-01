"""Tests for ResumeRunExecutor: stage gating and cached-dep wiring."""

from dataclasses import replace
from pathlib import Path

import pytest

import squeaky_clean.application.evaluation.eval.resume.resume_run_executor as executor_mod
from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.cached_design_architecture import (
    CachedDesignArchitecture,
)
from squeaky_clean.application.evaluation.eval.resume.cached_orchestrate_module import (
    CachedOrchestrateModule,
)
from squeaky_clean.application.evaluation.eval.resume.resume_run_executor import ResumeRunExecutor
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.notation.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps

_NOTATION = "MODULE Calculator\nLAYER Domain\nCLASSES {}\n"
_SENTINEL = object()


class _FakePipeline:
    """Stand-in for RunEvalPipeline capturing the deps it was built with."""

    captured: list[RunEvalDependencies] = []

    def __init__(self, deps: RunEvalDependencies) -> None:
        type(self).captured.append(deps)

    def run(self, problem: object, run_dir: Path) -> object:
        del problem, run_dir
        return _SENTINEL


@pytest.fixture(autouse=True)
def _fake_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    _FakePipeline.captured = []
    monkeypatch.setattr(executor_mod, "RunEvalPipeline", _FakePipeline)


def _impls_file(tmp_path: Path) -> Path:
    cls = ClassSpec(name="Operand", pattern="ValueObject", implements=None,
                    methods=(), depends=(), concretes=())
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(cls,), invariants=())
    ic = ImplementedClass(class_name="Operand", file_path="src/operand.py",
                          code="class Operand: ...", test_code=None,
                          cost_usd=0.1, duration_ms=100,
                          input_tokens=10, output_tokens=20)
    impl = ModuleImplementation(module=module, implemented_classes=(ic,),
                                total_cost_usd=0.1, total_duration_ms=100,
                                total_input_tokens=10, total_output_tokens=20,
                                wall_duration_ms=0)
    path = tmp_path / "impls.json"
    path.write_text(ModuleImplementationSerializer().serialize((impl,)))
    return path


def test_non_resumable_stage_falls_back_to_full_run(tmp_path: Path) -> None:
    """architect_done is before the resumable window → full restart, deps as-is."""
    deps = build_stub_deps()
    cp = RunCheckpoint(stage="architect_done")
    bundle = ResumeRunExecutor(deps, cp).resume(P0, tmp_path)
    assert bundle is _SENTINEL
    assert _FakePipeline.captured == [deps]


def test_icps_done_resumes_with_cached_stages_and_seeded_cost(tmp_path: Path) -> None:
    gate = CostGate()
    deps = replace(build_stub_deps(), cost_gate=gate)
    cp = RunCheckpoint(
        stage="icps_done", architecture_notation=_NOTATION,
        module_implementations_path=str(_impls_file(tmp_path)),
        cost_spent_usd=0.4,
    )
    bundle = ResumeRunExecutor(deps, cp).resume(P0, tmp_path)
    assert bundle is _SENTINEL
    stubbed = _FakePipeline.captured[0]
    assert stubbed is not deps
    assert isinstance(stubbed.design_architecture, CachedDesignArchitecture)
    assert isinstance(stubbed.orchestrate_module, CachedOrchestrateModule)
    # Checkpointed spend must carry into the resumed run's budget (R0.5).
    assert gate.spent_usd() == pytest.approx(0.4)


def test_resumable_stage_without_notation_raises(tmp_path: Path) -> None:
    deps = build_stub_deps()
    cp = RunCheckpoint(stage="tested", architecture_notation="",
                       module_implementations_path="ignored")
    with pytest.raises(ValueError, match="architecture_notation"):
        ResumeRunExecutor(deps, cp).resume(P0, tmp_path)
    assert _FakePipeline.captured == []
