"""Tests for SpecConformanceChecker method-drift detection."""

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.spec_conformance_checker import (
    SpecConformanceChecker,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _impl(methods: tuple[str, ...], code: str) -> ModuleImplementation:
    spec = ClassSpec(name="C", pattern="Entity", implements=None,
                     methods=methods, depends=(), concretes=())
    mod = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(spec,), invariants=())
    cls = ImplementedClass(class_name="C", file_path="c.py", code=code,
                           test_code=None, cost_usd=0.0, duration_ms=0,
                           input_tokens=0, output_tokens=0)
    return ModuleImplementation(
        module=mod, implemented_classes=(cls,), total_cost_usd=0.0,
        total_duration_ms=0, total_input_tokens=0, total_output_tokens=0,
        wall_duration_ms=0)


def test_present_method_is_conformant() -> None:
    impl = _impl(("handlePost(b: str): R",), "def handlePost(self, b): ...")
    assert SpecConformanceChecker().check(impl) == ()


def test_renamed_method_is_flagged() -> None:
    impl = _impl(("handlePost(b: str): R",), "def handle(self, b): ...")
    violations = SpecConformanceChecker().check(impl)
    assert len(violations) == 1
    assert "handlePost" in violations[0]


def test_matching_is_convention_agnostic() -> None:
    # declared camelCase, emitted snake_case -> still conformant
    impl = _impl(("findById(i: str): R",), "def find_by_id(self, i): ...")
    assert SpecConformanceChecker().check(impl) == ()


def test_no_declared_methods_is_conformant() -> None:
    assert SpecConformanceChecker().check(_impl((), "class C: pass")) == ()
