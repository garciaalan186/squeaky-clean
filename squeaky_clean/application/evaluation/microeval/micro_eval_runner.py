"""MicroEvalRunner: emit one squib fixture's classes and compile them (R5.4)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.evaluation.microeval.micro_eval_cell import MicroEvalCell
from squeaky_clean.application.evaluation.microeval.micro_eval_deps import MicroEvalDeps
from squeaky_clean.application.generation.emission.assign_patterns import AssignPatterns
from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class MicroEvalRunner:
    """One cell = parse fixture -> real routing -> real emitters -> compile.

    The middle tier between unit tests (stop at the LLM seam) and full
    benchmark problems: a handful of LLM calls plus one compiler invocation
    verifies that a pattern's emitters produce COMPILING code in a language
    (the R0.11 defect class). All sibling classes of the fixture module are
    emitted together so cross-class contracts (implements/extends) are
    exercised, not just single-file syntax.
    """

    def __init__(self, deps: MicroEvalDeps) -> None:
        self._deps = deps
        self._parser = ParseArchitectureNotation()
        self._toolkits = LanguageToolkitFactory()

    def run_cell(self, fixture: Path, language: TargetLanguage) -> MicroEvalCell:
        """Emit + compile one fixture for one language; never raises."""
        pattern = fixture.stem
        compiler = self._deps.compilers.get(language.value)
        if compiler is None or language.value not in self._deps.implementers:
            return MicroEvalCell(pattern, language.value, False, 0, 0, 0.0,
                                 "no compiler/implementer for language")
        try:
            return self._emit_and_compile(fixture, language, compiler)
        except Exception as exc:  # noqa: BLE001 — cell isolation
            return MicroEvalCell(pattern, language.value, False, 0, 0, 0.0,
                                 f"{type(exc).__name__}: {exc}")

    def _emit_and_compile(
        self, fixture: Path, language: TargetLanguage, compiler: ProjectCompiler,
    ) -> MicroEvalCell:
        pattern = fixture.stem
        cell_dir = self._deps.out_root / f"{pattern}-{language.value}"
        module = self._parser.parse(fixture.read_text()).modules[0]
        toolkit = self._toolkits.for_language(language)
        assignments = AssignPatterns(toolkit, cell_dir).assign_all(module)
        implementer = self._deps.implementers[language.value]
        cost = 0.0
        for assignment in assignments:
            implemented = implementer.execute(assignment)
            cost += implemented.cost_usd
            target = cell_dir / implemented.file_path
            atomic_write_text(target, implemented.code)
        for name, content in self._deps.extra_files.get(
            language.value, {},
        ).items():
            atomic_write_text(cell_dir / name, content)
        result = compiler.compile(cell_dir)
        return MicroEvalCell(
            pattern=pattern, language=language.value, passed=result.ok,
            compile_errors=result.error_count,
            classes_emitted=len(assignments), cost_usd=cost,
            detail="" if result.ok else result.raw_output[:400],
        )
