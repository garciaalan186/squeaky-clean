"""Tests for CachedDesignArchitecture (cached stand-in, no LLM call)."""

from eval.problems.p0_calculator import P0
from squeaky_clean.application.evaluation.eval.resume.cached_design_architecture import (
    CachedDesignArchitecture,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _arch() -> ArchitectureSpec:
    module = ModuleSpec(name="Calculator", layer=LayerType.DOMAIN, exports=(),
                        depends=(), classes=(), invariants=())
    return ArchitectureSpec(modules=(module,), graph=ArchitectureGraph(edges={}))


def test_cached_design_architecture_ignores_problem() -> None:
    arch = _arch()
    stub = CachedDesignArchitecture(arch)
    assert stub.execute(P0) is arch
    assert stub.last_raw_notation == ""
