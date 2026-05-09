"""Tests for the IntegrationRequest DTO."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.integration_request import IntegrationRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module() -> ModuleSpec:
    cls = ClassSpec(
        name="Foo",
        pattern="SimpleClass",
        implements=None,
        methods=("bar()",),
        depends=(),
        concretes=(),
    )
    return ModuleSpec(
        name="M",
        layer=LayerType.DOMAIN,
        exports=(),
        depends=(),
        classes=(cls,),
        invariants=(),
    )


def test_integration_request_is_frozen() -> None:
    impl = ModuleImplementation(
        module=_module(),
        implemented_classes=(
            ImplementedClass(
                class_name="Foo",
                file_path="src/foo.py",
                code="class Foo: pass\n",
                test_code=None,
                cost_usd=0.0,
                duration_ms=0,
                input_tokens=0,
                output_tokens=0,
            ),
        ),
        total_cost_usd=0.0,
        total_duration_ms=0,
        total_input_tokens=0,
        total_output_tokens=0,
    wall_duration_ms=0,
    )
    test_arch = TestArchitecture(gherkin_scenarios=(), test_skeletons=())
    req = IntegrationRequest(
        implementation=impl,
        test_architecture=test_arch,
        output_dir=Path("/tmp/out"),
    )
    assert req.output_dir == Path("/tmp/out")
    with pytest.raises(FrozenInstanceError):
        setattr(req, "output_dir", Path("/other"))  # noqa: B010
