"""Tests for AssignPatterns use case."""

from pathlib import Path

from squeaky_clean.application.use_cases.assign_patterns import AssignPatterns
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _module() -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Operand", "CalculatorService"),
        depends=(),
        classes=(
            ClassSpec(
                name="Operand",
                pattern="ValueObject",
                implements=None,
                methods=(),
                depends=(),
                concretes=(),
            ),
            ClassSpec(
                name="CalculatorService",
                pattern="Facade",
                implements=None,
                methods=(),
                depends=(),
                concretes=(),
            ),
        ),
        invariants=(),
    )


def test_assign_all_returns_one_per_class() -> None:
    module = _module()
    assigner = AssignPatterns(_PY, Path("/tmp/out"))
    assignments = assigner.assign_all(module)
    assert len(assignments) == 2
    by_name = {a.class_spec.name: a for a in assignments}
    assert by_name["Operand"].icp_spec_name == "python/ddd_clean/ValueObjectICP"
    assert by_name["Operand"].file_path == (
        "/tmp/out/src/domain/calculator/operand.py"
    )
    assert by_name["Operand"].test_file_path == (
        "/tmp/out/tests/domain/calculator/test_operand.py"
    )
    assert (
        by_name["CalculatorService"].icp_spec_name
        == "python/ddd_clean/SimpleClassICP"
    )
    assert by_name["CalculatorService"].file_path.endswith(
        "/src/domain/calculator/calculator_service.py"
    )


def test_assign_all_populates_module() -> None:
    module = _module()
    assigner = AssignPatterns(_PY, Path("/tmp/out"))
    assignments = assigner.assign_all(module)
    for assignment in assignments:
        assert assignment.module is module
