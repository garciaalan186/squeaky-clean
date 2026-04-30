"""Tests for the IntegrateModule use case."""

from pathlib import Path

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.integration_request import IntegrationRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_skeleton import TestSkeleton
from squeaky_clean.application.use_cases.integrate_module import IntegrateModule
from squeaky_clean.application.use_cases.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def _module() -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=(),
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
        ),
        invariants=(),
    )


def test_integrate_module_writes_files(tmp_path: Path) -> None:
    impl = ImplementedClass(
        class_name="Operand",
        file_path="src/domain/calculator/operand.py",
        code="class Operand:\n    pass\n",
        test_code=None,
        cost_usd=0.0,
        duration_ms=0,
        input_tokens=0,
        output_tokens=0,
    )
    skeleton = TestSkeleton(
        class_name="Operand",
        file_path="tests/domain/calculator/test_operand.py",
        code="def test_placeholder():\n    pass\n",
    )
    mi = ModuleImplementation(
        module=_module(),
        implemented_classes=(impl,),
        total_cost_usd=0.0,
        total_duration_ms=0,
        total_input_tokens=0,
        total_output_tokens=0,
    wall_duration_ms=0,
    )
    test_arch = TestArchitecture(
        gherkin_scenarios=(), test_skeletons=(skeleton,)
    )
    req = IntegrationRequest(
        implementation=mi, test_architecture=test_arch, output_dir=tmp_path
    )
    fs = LocalFileSystem()
    result = IntegrateModule(fs, PythonIntegrationBootstrap(fs)).execute(req)
    assert (tmp_path / "src" / "domain" / "calculator" / "operand.py").exists()
    assert (tmp_path / "src" / "__init__.py").exists()
    assert (tmp_path / "src" / "domain" / "__init__.py").exists()
    assert (tmp_path / "src" / "domain" / "calculator" / "__init__.py").exists()
    assert (tmp_path / "tests" / "__init__.py").exists()
    assert (tmp_path / "tests" / "domain" / "__init__.py").exists()
    assert (tmp_path / "tests" / "conftest.py").exists()
    assert (tmp_path / "tests" / "domain" / "calculator" / "test_operand.py").exists()
    assert len(result.files_written) == 1
    assert len(result.test_files_written) == 1
