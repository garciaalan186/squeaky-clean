"""Tests for ClassAssignment DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.use_cases.language_toolkit_factory import LanguageToolkitFactory
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_TOOLKIT = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _spec() -> ClassSpec:
    return ClassSpec(
        name="Operand",
        pattern="ValueObject",
        implements=None,
        methods=(),
        depends=(),
        concretes=(),
    )


def _module(spec: ClassSpec) -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=(spec.name,),
        depends=(),
        classes=(spec,),
        invariants=(),
    )


def test_class_assignment_stores_fields() -> None:
    spec = _spec()
    assignment = ClassAssignment(
        class_spec=spec,
        module=_module(spec),
        toolkit=_TOOLKIT,
        icp_spec_name="ValueObjectICP",
        file_path="src/operand.py",
        test_file_path="tests/test_operand.py",
    )
    assert assignment.icp_spec_name == "ValueObjectICP"
    assert assignment.class_spec.name == "Operand"
    assert assignment.module.name == "Calculator"


def test_class_assignment_is_frozen() -> None:
    spec = _spec()
    assignment = ClassAssignment(
        class_spec=spec,
        module=_module(spec),
        toolkit=_TOOLKIT,
        icp_spec_name="ValueObjectICP",
        file_path="src/operand.py",
        test_file_path="tests/test_operand.py",
    )
    with pytest.raises(FrozenInstanceError):
        assignment.icp_spec_name = "Other"  # type: ignore[misc]
