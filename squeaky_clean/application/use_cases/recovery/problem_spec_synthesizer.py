"""ProblemSpecSynthesizer: build a thin ProblemSpec from a recovered spec."""

import ast
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


class ProblemSpecSynthesizer:
    """Synthesizes the ProblemSpec that drives Stage-6 regeneration.

    The recovered ArchitectureSpec fixes the module/class counts, bounded
    contexts, and required patterns so downstream conformance passes on
    the very spec it was built from. Acceptance criteria are derived from
    the legacy ``tests/`` directory — one per discovered ``def test_*`` —
    so the regenerated project is checked against the behaviour the
    original code encoded.
    """

    def synthesize(
        self, spec: ArchitectureSpec, tests_dir: Path | None = None,
    ) -> ProblemSpec:
        """Return a thin ProblemSpec that regenerates ``spec``."""
        classes = [c for m in spec.modules for c in m.classes]
        modules = len(spec.modules)
        return ProblemSpec(
            id="RECOVERED", tier=0, slug="recovered",
            description="Regenerated from a recovered, human-reviewed architecture.",
            required_bounded_contexts=[m.name for m in spec.modules],
            acceptance_criteria=self._criteria(tests_dir),
            expected_module_count=(modules, modules),
            expected_class_count=(len(classes), len(classes)),
            required_patterns=sorted({c.pattern for c in classes}),
            target_language=TargetLanguage.PYTHON,
        )

    def _criteria(self, tests_dir: Path | None) -> list[str]:
        if tests_dir is None or not tests_dir.exists():
            return []
        out: list[str] = []
        for path in sorted(tests_dir.rglob("test_*.py")):
            out.extend(self._from_file(path))
        return out

    def _from_file(self, path: Path) -> list[str]:
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, UnicodeDecodeError):
            return []
        return [
            node.name[len("test_"):].replace("_", " ")
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        ]
