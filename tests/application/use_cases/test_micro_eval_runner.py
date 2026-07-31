"""Tests for MicroEvalRunner (R5.4) — stub emitter, fake compiler, no LLM."""

from pathlib import Path

from squeaky_clean.application.evaluation.microeval.micro_eval_deps import (
    MicroEvalDeps,
)
from squeaky_clean.application.evaluation.microeval.micro_eval_runner import (
    MicroEvalRunner,
)
from squeaky_clean.application.generation.emission.implemented_class import (
    ImplementedClass,
)
from squeaky_clean.domain.value_objects.compile_result import CompileResult
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_SQUIB = """MODULE Discounts
LAYER Domain
EXPORTS [DiscountStrategy]
DEPENDS []
CLASSES {
  DiscountStrategy -> Strategy {
    methods: [apply(total: float): float]
    concretes: [PercentageDiscount]
  }
  PercentageDiscount -> Strategy {
    methods: [apply(total: float): float]
    depends: [DiscountStrategy]
  }
}
"""


class _StubImplementer:
    def __init__(self, code: str = "class Ok:\n    pass\n") -> None:
        self._code = code

    def execute(self, assignment):  # noqa: ANN001, ANN201 — duck-typed stub
        return ImplementedClass(
            class_name=assignment.class_spec.name,
            file_path=f"src/{assignment.class_spec.name.lower()}.py",
            code=self._code, test_code=None, cost_usd=0.001,
            duration_ms=1, input_tokens=10, output_tokens=10,
        )


class _FakeCompiler:
    def __init__(self, ok: bool) -> None:
        self._ok = ok

    def compile(self, project_dir: Path) -> CompileResult:
        return CompileResult(
            ok=self._ok, error_count=0 if self._ok else 3,
            offending_stems=(), raw_output="" if self._ok else "boom",
        )


def _fixture(tmp_path: Path) -> Path:
    fx = tmp_path / "strategy.squib"
    fx.write_text(_SQUIB)
    return fx


def _deps(tmp_path: Path, ok: bool) -> MicroEvalDeps:
    return MicroEvalDeps(
        implementers={"python": _StubImplementer()},  # type: ignore[dict-item]
        compilers={"python": _FakeCompiler(ok)},  # type: ignore[dict-item]
        out_root=tmp_path / "out",
        extra_files={"python": {"marker.txt": "x"}},
    )


def test_cell_emits_all_classes_and_passes(tmp_path: Path) -> None:
    runner = MicroEvalRunner(_deps(tmp_path, ok=True))
    cell = runner.run_cell(_fixture(tmp_path), TargetLanguage.PYTHON)
    assert cell.passed and cell.classes_emitted == 2
    assert abs(cell.cost_usd - 0.002) < 1e-9
    cell_dir = tmp_path / "out" / "strategy-python"
    assert (cell_dir / "marker.txt").read_text() == "x"
    assert (cell_dir / "src" / "discountstrategy.py").is_file()


def test_compile_failure_fails_cell_with_detail(tmp_path: Path) -> None:
    runner = MicroEvalRunner(_deps(tmp_path, ok=False))
    cell = runner.run_cell(_fixture(tmp_path), TargetLanguage.PYTHON)
    assert not cell.passed and cell.compile_errors == 3
    assert "boom" in cell.detail


def test_missing_language_adapter_fails_loudly(tmp_path: Path) -> None:
    runner = MicroEvalRunner(_deps(tmp_path, ok=True))
    cell = runner.run_cell(_fixture(tmp_path), TargetLanguage.JAVA)
    assert not cell.passed
    assert "no compiler/implementer" in cell.detail


def test_exception_is_isolated_to_the_cell(tmp_path: Path) -> None:
    class _Boom:
        def execute(self, assignment):  # noqa: ANN001, ANN201
            raise RuntimeError("gateway down")

    deps = MicroEvalDeps(
        implementers={"python": _Boom()},  # type: ignore[dict-item]
        compilers={"python": _FakeCompiler(True)},  # type: ignore[dict-item]
        out_root=tmp_path / "out",
    )
    cell = MicroEvalRunner(deps).run_cell(
        _fixture(tmp_path), TargetLanguage.PYTHON,
    )
    assert not cell.passed
    assert "RuntimeError" in cell.detail
