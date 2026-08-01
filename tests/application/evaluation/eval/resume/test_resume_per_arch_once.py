"""Tests for PerArchOnce: cached TestArchitecture gate keyed to the first module."""

from squeaky_clean.application.evaluation.eval.resume.resume_per_arch_once import PerArchOnce
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_CACHED = TestArchitecture(gherkin_scenarios=("Feature: cached",), test_skeletons=())


def _module(name: str) -> ModuleSpec:
    return ModuleSpec(name=name, layer=LayerType.DOMAIN, exports=(),
                      depends=(), classes=(), invariants=())


def _arch(*modules: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(modules=modules, graph=ArchitectureGraph(edges={}))


def test_first_module_receives_cached_value() -> None:
    first, second = _module("Auth"), _module("Cart")
    gate = PerArchOnce(_CACHED, _arch(first, second))
    assert gate.take(first) is _CACHED


def test_later_modules_receive_empty_architecture() -> None:
    first, second = _module("Auth"), _module("Cart")
    gate = PerArchOnce(_CACHED, _arch(first, second))
    result = gate.take(second)
    assert result.gherkin_scenarios == ()
    assert result.test_skeletons == ()


def test_gate_matches_by_module_name_and_is_repeatable() -> None:
    gate = PerArchOnce(_CACHED, _arch(_module("Auth"), _module("Cart")))
    # A distinct ModuleSpec instance with the same name still hits the cache,
    # and asking again does not exhaust it.
    assert gate.take(_module("Auth")) is _CACHED
    assert gate.take(_module("Auth")) is _CACHED


def test_empty_architecture_never_returns_cached() -> None:
    gate = PerArchOnce(_CACHED, _arch())
    assert gate.take(_module("Auth")).gherkin_scenarios == ()
