"""Tests for PortMethodDecomposer (H2)."""

from __future__ import annotations

from squeaky_clean.application.use_cases.port_method_decomposer import (
    decompose_class,
    decompose_module_for_tier_c,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, methods: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="Adapter", implements=None,
        methods=methods, depends=(), concretes=(),
        fields=(), invariants=(),
    )


def test_five_methods_passes_through() -> None:
    c = _cls("X", ("a()", "b()", "c()", "d()", "e()"))
    out = decompose_class(c)
    assert len(out) == 1
    assert out[0] is c


def test_six_methods_splits_3_3_plus_facade() -> None:
    c = _cls("Repo", ("a()", "b()", "c()", "d()", "e()", "f()"))
    out = decompose_class(c)
    assert len(out) == 3  # 2 collaborators + facade
    assert out[-1].name == "Repo"
    assert out[-1].pattern == "Facade"
    assert len(out[0].methods) == 3 and len(out[1].methods) == 3


def test_seven_methods_splits_4_3_plus_facade() -> None:
    c = _cls("X", ("a()", "b()", "c()", "d()", "e()", "f()", "g()"))
    out = decompose_class(c)
    assert len(out) == 3
    assert len(out[0].methods) == 4 and len(out[1].methods) == 3


def test_nine_methods_splits_4_4_1_plus_facade() -> None:
    methods = tuple(f"m{i}()" for i in range(9))
    c = _cls("Big", methods)
    out = decompose_class(c)
    assert len(out) == 4  # 3 collaborators + facade
    assert sum(len(s.methods) for s in out[:-1]) == 9


def test_facade_depends_on_collaborators() -> None:
    c = _cls("Y", ("a()", "b()", "c()", "d()", "e()", "f()"))
    out = decompose_class(c)
    facade = out[-1]
    assert set(facade.depends) == {out[0].name, out[1].name}


def test_decompose_module_only_touches_tier_c_names() -> None:
    big = _cls("BigAdapter", ("a()", "b()", "c()", "d()", "e()", "f()", "g()"))
    small = _cls("Other", ("a()",))
    mod = ModuleSpec(
        name="M", layer=LayerType.INFRASTRUCTURE, exports=(),
        depends=(), classes=(big, small), invariants=(),
    )
    out = decompose_module_for_tier_c(mod, frozenset({"BigAdapter"}))
    assert len(out.classes) == 4  # 2 collaborators + facade + small unchanged
    assert any(c.name == "Other" for c in out.classes)


def test_decompose_module_no_tier_c_passes_through() -> None:
    c = _cls("X", ("a()", "b()", "c()", "d()", "e()", "f()", "g()"))
    mod = ModuleSpec(
        name="M", layer=LayerType.INFRASTRUCTURE, exports=(),
        depends=(), classes=(c,), invariants=(),
    )
    out = decompose_module_for_tier_c(mod, frozenset())
    assert out.classes == (c,)
