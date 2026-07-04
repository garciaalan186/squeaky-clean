"""Unit tests for architecture_spec_rules (spec-level validation)."""

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, *, methods: tuple[str, ...] = (), invariants: tuple[str, ...] = ()) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="SimpleClass", implements=None,
        methods=methods, depends=(), concretes=(),
        fields=(), invariants=invariants,
    )


def _spec(*classes: ClassSpec) -> ArchitectureSpec:
    mod = ModuleSpec(
        name="M", layer=LayerType.DOMAIN, exports=tuple(c.name for c in classes),
        depends=(), classes=tuple(classes), invariants=(),
    )
    return ArchitectureSpec(modules=(mod,), graph=ArchitectureGraph(edges={}))


def test_empty_class_with_no_methods_no_invariants_violates() -> None:
    spec = _spec(_cls("Operand"))
    issues = spec.validate()
    assert any("Operand has no methods and no invariants" in v for v in issues)
    assert any("rule 13" in v for v in issues)


def test_class_with_only_methods_is_valid() -> None:
    spec = _spec(_cls("Calc", methods=("add(): int",)))
    assert spec.validate() == ()


def test_class_with_only_invariants_is_valid() -> None:
    spec = _spec(_cls("Title", invariants=("must be non-empty",)))
    assert spec.validate() == ()


def test_six_methods_at_spec_time_flagged() -> None:
    spec = _spec(_cls("Big", methods=tuple(f"m{i}()" for i in range(6))))
    issues = spec.validate()
    assert any("declares 6 methods" in v for v in issues)
    assert any("Strategy or Facade" in v for v in issues)


def test_five_methods_at_spec_time_ok() -> None:
    spec = _spec(_cls("OK", methods=tuple(f"m{i}()" for i in range(5))))
    assert spec.validate() == ()


def test_decorative_vo_alongside_real_class_only_decorative_flagged() -> None:
    spec = _spec(
        _cls("Operand"),  # decorative
        _cls("Calculator", methods=("add(): int",)),  # real
    )
    issues = spec.validate()
    flagged = [v for v in issues if "rule 13" in v]
    assert len(flagged) == 1
    assert "Operand" in flagged[0]
