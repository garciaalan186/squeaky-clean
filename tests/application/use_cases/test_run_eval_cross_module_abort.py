"""Integration test: pipeline aborts on cross-module dep violations before ICP fan-out."""

from dataclasses import replace
from pathlib import Path

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.cross_module_dependency_error import (
    CrossModuleDependencyError,
)
from squeaky_clean.application.use_cases.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from tests.application.use_cases.run_eval_stub_deps import build_stub_deps


def _broken_arch() -> ArchitectureSpec:
    cls = ClassSpec(
        name="Op", pattern="SimpleClass", implements=None,
        methods=(), depends=("GhostMod::GhostType",), concretes=(),
    )
    module = ModuleSpec(
        name="Calculator", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )
    return ArchitectureSpec(
        modules=(module,), graph=ArchitectureGraph(edges={}),
    )


def test_pipeline_aborts_with_cross_module_error(tmp_path: Path) -> None:
    deps = build_stub_deps()
    broken = _broken_arch()

    def _design(_p: ProblemSpec) -> ArchitectureSpec:
        return broken

    deps.design_architecture.execute = _design  # type: ignore[assignment,method-assign]
    pipeline = RunEvalPipeline(replace(deps))
    with pytest.raises(CrossModuleDependencyError) as ei:
        pipeline.run(P0, tmp_path)
    assert ei.value.violations
    assert any("GhostMod" in v for v in ei.value.violations)
    deps.orchestrate_module.execute.assert_not_called()  # type: ignore[attr-defined]
    deps.integrate_module.execute.assert_not_called()  # type: ignore[attr-defined]
    assert (tmp_path / "CROSS_MODULE_VIOLATIONS.txt").exists()
    body = (tmp_path / "CROSS_MODULE_VIOLATIONS.txt").read_text()
    assert "GhostMod" in body
