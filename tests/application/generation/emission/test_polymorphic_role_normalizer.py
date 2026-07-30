"""Tests for PolymorphicRoleNormalizer (R0.11)."""

from squeaky_clean.application.generation.emission.polymorphic_role_normalizer import (
    PolymorphicRoleNormalizer,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str, pattern: str, depends: tuple[str, ...] = (),
         concretes: tuple[str, ...] = (), implements: str | None = None) -> ClassSpec:
    return ClassSpec(
        name=name, pattern=pattern, implements=implements,  # type: ignore[arg-type]
        methods=("apply(total: float): float",), depends=depends,
        concretes=concretes,
    )


def _module(*classes: ClassSpec) -> ModuleSpec:
    return ModuleSpec(
        name="Cart", layer=LayerType.DOMAIN, exports=(),
        depends=(), classes=classes, invariants=(),
    )


def test_depends_shape_stamps_implements_and_concretes() -> None:
    # The P2JAVA/P2TS shape: abstract Strategy with empty concretes; the
    # concretes reference it via depends only.
    mod = PolymorphicRoleNormalizer().normalize(_module(
        _cls("DiscountStrategy", "Strategy"),
        _cls("PercentageDiscount", "Strategy", depends=("DiscountStrategy",)),
        _cls("FixedAmountDiscount", "Strategy", depends=("DiscountStrategy",)),
    ))
    by = {c.name: c for c in mod.classes}
    assert by["DiscountStrategy"].concretes == (
        "PercentageDiscount", "FixedAmountDiscount",
    )
    assert by["PercentageDiscount"].implements == "DiscountStrategy"
    assert by["FixedAmountDiscount"].implements == "DiscountStrategy"


def test_canonical_shape_is_untouched() -> None:
    mod = _module(
        _cls("Processor", "Strategy", concretes=("CardProcessor",)),
        _cls("CardProcessor", "Strategy", implements="Processor",
             depends=("Processor",)),
    )
    assert PolymorphicRoleNormalizer().normalize(mod) == mod


def test_non_polymorphic_pattern_depends_untouched() -> None:
    # Entity -> Entity depends must NOT be read as abstract/concrete.
    mod = _module(
        _cls("Order", "Entity"),
        _cls("OrderLine", "Entity", depends=("Order",)),
    )
    assert PolymorphicRoleNormalizer().normalize(mod) == mod


def test_cross_pattern_depends_untouched() -> None:
    # Entity depending on a Strategy is a collaborator, not a concrete.
    mod = _module(
        _cls("DiscountStrategy", "Strategy"),
        _cls("Cart", "Entity", depends=("DiscountStrategy",)),
    )
    assert PolymorphicRoleNormalizer().normalize(mod) == mod


def test_declared_concretes_merge_without_duplicates() -> None:
    mod = PolymorphicRoleNormalizer().normalize(_module(
        _cls("Handler", "ChainOfResponsibility", concretes=("AuthHandler",)),
        _cls("AuthHandler", "ChainOfResponsibility", depends=("Handler",)),
        _cls("LogHandler", "ChainOfResponsibility", depends=("Handler",)),
    ))
    by = {c.name: c for c in mod.classes}
    assert by["Handler"].concretes == ("AuthHandler", "LogHandler")
