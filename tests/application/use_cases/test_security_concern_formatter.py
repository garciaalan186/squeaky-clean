"""Tests for SecurityConcernFormatter."""

from squeaky_clean.application.dtos.security_concern import SecurityConcern
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.application.use_cases.security_concern_formatter import (
    SecurityConcernFormatter,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_CLS = ClassSpec(
    name="Calculator", pattern="SimpleClass", implements=None,
    methods=("add(a: float, b: float): float",),
    depends=(), concretes=(), fields=("a: float", "b: float"),
)
_CONCERN = SecurityConcern(
    category="input_validation", target_class="Calculator",
    description="No validation on add()", test_scenario="Pass None to add()",
)
_FMT = SecurityConcernFormatter()


def test_format_contains_concern_fields() -> None:
    result = _FMT.format(_CONCERN, _CLS)
    assert "CONCERN input_validation" in result
    assert "TARGET_CLASS Calculator" in result
    assert "TARGET_FILE calculator" in result
    assert "DESCRIPTION No validation on add()" in result
    assert "TEST_SCENARIO Pass None to add()" in result


def test_format_contains_class_fields_and_methods() -> None:
    result = _FMT.format(_CONCERN, _CLS)
    assert "a: float, b: float" in result
    assert "add(a: float, b: float): float" in result


def test_format_handles_empty_fields() -> None:
    cls = ClassSpec(
        name="Empty", pattern="SimpleClass", implements=None,
        methods=(), depends=(), concretes=(), fields=(),
    )
    result = _FMT.format(_CONCERN, cls)
    assert "(none)" in result


def test_format_with_toolkit_uses_correct_case() -> None:
    tk = LanguageToolkitFactory().for_language(TargetLanguage.JAVASCRIPT)
    fmt = SecurityConcernFormatter(toolkit=tk)
    result = fmt.format(_CONCERN, _CLS)
    assert "TARGET_FILE calculator" in result


def test_format_includes_depends_files() -> None:
    cls = ClassSpec(
        name="OrderService", pattern="SimpleClass", implements=None,
        methods=("place(): void",), depends=("Product", "Customer"),
        concretes=(), fields=(),
    )
    concern = SecurityConcern(
        category="input_validation", target_class="OrderService",
        description="No validation", test_scenario="Pass None",
    )
    result = _FMT.format(concern, cls)
    assert "DEPENDS_FILES Product=product, Customer=customer" in result


def test_format_no_depends_files_when_empty() -> None:
    result = _FMT.format(_CONCERN, _CLS)
    assert "DEPENDS_FILES" not in result


def test_format_emits_dotted_path_when_module_supplied() -> None:
    from squeaky_clean.domain.entities.module_spec import ModuleSpec
    from squeaky_clean.domain.value_objects.layer_type import LayerType
    tk = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    cls = ClassSpec(
        name="OrderService", pattern="SimpleClass", implements=None,
        methods=("place(): void",), depends=("Product",),
        concretes=(), fields=(),
    )
    module = ModuleSpec(
        name="Orders", layer=LayerType.APPLICATION, exports=(),
        depends=(), classes=(cls,), invariants=(),
    )
    concern = SecurityConcern(
        category="input_validation", target_class="OrderService",
        description="d", test_scenario="t",
    )
    fmt = SecurityConcernFormatter(toolkit=tk, module=module)
    result = fmt.format(concern, cls)
    assert "TARGET_FILE src.application.orders.order_service" in result
    assert "DEPENDS_FILES Product=src.application.orders.product" in result
