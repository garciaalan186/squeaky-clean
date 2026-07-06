"""Tests for CompileGate: compile-then-fix retry loop."""

from pathlib import Path

from squeaky_clean.application.dtos.compile_result import CompileResult
from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.compile_gate import (
    CompileGate,
    CompileGateRequest,
)
from squeaky_clean.application.use_cases.fixer_stage import (
    FixerStage,
    FixerStageResult,
)
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.layer_type import LayerType


class _FakeCompiler(ProjectCompiler):
    def __init__(self, results: list[CompileResult]) -> None:
        self._results = results

    def compile(self, project_dir: Path) -> CompileResult:
        return self._results.pop(0) if len(self._results) > 1 else self._results[0]


class _FakeFixer(FixerStage):
    def __init__(self, fixed: int) -> None:
        super().__init__(None, None)
        self._fixed = fixed
        self.calls = 0

    def apply(self, request: FixRequest, output_dir: Path) -> FixerStageResult:
        self.calls += 1
        return FixerStageResult(self._fixed, 0, 0, 0.0, 0, 1)


def _impl() -> ModuleImplementation:
    mod = ModuleSpec(name="M", layer=LayerType.DOMAIN, exports=(),
                     depends=(), classes=(), invariants=())
    return ModuleImplementation(
        module=mod, implemented_classes=(), total_cost_usd=0.0,
        total_duration_ms=0, total_input_tokens=0, total_output_tokens=0,
        wall_duration_ms=0,
    )


def _req() -> CompileGateRequest:
    return CompileGateRequest(_impl(), Path("/tmp/x"), max_passes=2)


def _fail() -> CompileResult:
    return CompileResult(False, 2, ("A",), "err")


def _ok() -> CompileResult:
    return CompileResult(True, 0, (), "")


def test_no_compiler_is_a_noop() -> None:
    result = CompileGate(None, _FakeFixer(0)).run(_req())
    assert result.compile_errors == 0


def test_clean_compile_skips_fixer() -> None:
    fixer = _FakeFixer(1)
    result = CompileGate(_FakeCompiler([_ok()]), fixer).run(_req())
    assert result.compile_errors == 0
    assert fixer.calls == 0


def test_fix_then_recompile_clears_errors() -> None:
    fixer = _FakeFixer(1)
    gate = CompileGate(_FakeCompiler([_fail(), _ok()]), fixer)
    result = gate.run(_req())
    assert fixer.calls == 1
    assert result.compile_errors == 0
    assert result.fixer.classes_fixed == 1


def test_stops_when_fixer_makes_no_progress() -> None:
    fixer = _FakeFixer(0)
    result = CompileGate(_FakeCompiler([_fail()]), fixer).run(_req())
    assert result.compile_errors == 2
    assert fixer.calls == 1
