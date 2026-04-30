"""Tests for FixerStage."""

from pathlib import Path
from typing import cast
from unittest.mock import Mock

from squeaky_clean.application.dtos.fix_result import FixResult
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.use_cases.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.use_cases.fixer_stage import FixerStage
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _impl() -> ModuleImplementation:
    spec = ClassSpec(name="Op", pattern="ValueObject", implements=None,
                     methods=(), depends=(), concretes=())
    module = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                       depends=(), classes=(spec,), invariants=())
    cls = ImplementedClass(
        class_name="Op", file_path="src/op.py", code="x",
        test_code=None, cost_usd=0, duration_ms=0,
        input_tokens=0, output_tokens=0,
    )
    return ModuleImplementation(
        module=module, implemented_classes=(cls,), total_cost_usd=0,
        total_duration_ms=0, total_input_tokens=0, total_output_tokens=0,
        wall_duration_ms=0,
    )


def _tr(failed: int) -> TestRunResult:
    return TestRunResult(
        passed=0, failed=failed, errors=0, duration_ms=1,
        raw_output="FAILED tests/test_op.py::test_a" if failed else "ok",
    )


def test_apply_noop_when_no_failures() -> None:
    fixer = cast(FixFailingClasses, Mock(spec=FixFailingClasses))
    fs = cast(ProjectFileSystem, Mock(spec=ProjectFileSystem))
    stage = FixerStage(fixer, fs)
    result = stage.apply(FixerStage.requested(_impl(), _tr(0)), Path("/tmp"))
    assert result.classes_fixed == 0


def test_apply_noop_when_fixer_not_wired() -> None:
    stage = FixerStage(None, None)
    result = stage.apply(FixerStage.requested(_impl(), _tr(1)), Path("/tmp"))
    assert result.classes_fixed == 0


def test_apply_dispatches_and_rewrites_files_on_failure() -> None:
    cls = _impl().implemented_classes[0]
    fixer = Mock(spec=FixFailingClasses)
    fixer.execute.return_value = FixResult(
        fixed_classes=(cls,), input_tokens=10, output_tokens=5,
        cost_usd=0.03, duration_ms=200,
    )
    fs = Mock(spec=ProjectFileSystem)
    stage = FixerStage(cast(FixFailingClasses, fixer), cast(ProjectFileSystem, fs))
    result = stage.apply(FixerStage.requested(_impl(), _tr(1)), Path("/tmp"))
    assert result.classes_fixed == 1
    assert result.cost_usd == 0.03
    assert fs.write.call_count == 1
