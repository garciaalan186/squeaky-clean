"""Tests for AssignPatternsPaths."""

from pathlib import Path

from squeaky_clean.application.use_cases.assign_patterns_paths import AssignPatternsPaths
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _module(name: str, layer: LayerType) -> ModuleSpec:
    return ModuleSpec(
        name=name, layer=layer, exports=(), depends=(),
        classes=(ClassSpec(
            name="X", pattern="SimpleClass", implements=None,
            methods=(), depends=(), concretes=(),
        ),),
        invariants=(),
    )


def test_python_paths_flat_when_no_module() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    paths = AssignPatternsPaths(toolkit, Path("/tmp/out"))
    src, test = paths.for_class("CalculatorService")
    assert src == Path("/tmp/out/src/calculator_service.py")
    assert test == Path("/tmp/out/tests/test_calculator_service.py")


def test_python_paths_layered_when_module_supplied() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    paths = AssignPatternsPaths(toolkit, Path("/tmp/out"))
    module = _module("AuthRepository", LayerType.APPLICATION)
    src, test = paths.for_class("UserRepository", module)
    assert src == Path("/tmp/out/src/application/auth_repository/user_repository.py")
    assert test == Path(
        "/tmp/out/tests/application/auth_repository/test_user_repository.py",
    )


def test_python_domain_module_layered() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    paths = AssignPatternsPaths(toolkit, Path("/tmp/out"))
    module = _module("Calculator", LayerType.DOMAIN)
    src, test = paths.for_class("Operand", module)
    assert src == Path("/tmp/out/src/domain/calculator/operand.py")
    assert test == Path("/tmp/out/tests/domain/calculator/test_operand.py")


def test_javascript_paths_camel_case_no_layering() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVASCRIPT)
    paths = AssignPatternsPaths(toolkit, Path("/tmp/out"))
    module = _module("Calc", LayerType.DOMAIN)
    src, test = paths.for_class("TodoRepository", module)
    assert src == Path("/tmp/out/src/todoRepository.js")
    assert test == Path("/tmp/out/tests/todoRepository.test.js")


def test_java_paths_pascal_case_no_layering() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    paths = AssignPatternsPaths(toolkit, Path("/tmp/out"))
    module = _module("Calc", LayerType.DOMAIN)
    src, test = paths.for_class("Calculator", module)
    assert src == Path("/tmp/out/src/main/java/Calculator.java")
    assert test == Path("/tmp/out/src/test/java/CalculatorTest.java")
