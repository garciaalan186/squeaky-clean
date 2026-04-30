"""ArchitecturalComplexityScorer: composite ACS per BENCHMARK_METHODOLOGY.md."""

from __future__ import annotations

import ast
from pathlib import Path

from squeaky_clean.application.dtos.complexity_score import ComplexityScore
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_ALPHA = (1.0, 0.5, 0.3, 0.4, 0.2)        # M, C, D, X, I
_BETA = (0.4, 0.001, 0.05, 0.5)            # H, N, V, E
_GAMMA = (1.0, 2.0, 1.0, 1.5)              # A, CC, DC, IC
_W = (0.5, 0.3, 0.2)                       # w_S, w_G, w_P
_BASELINE = 2.5                            # P0 Calculator ACS (calibrated 2026-04-28)


class ArchitecturalComplexityScorer:
    """Compute the composite ACS for a (problem, arch, source_dir) triple."""

    def score(
        self, problem: ProblemSpec, arch: ArchitectureSpec,
        source_dir: Path | None = None,
    ) -> ComplexityScore:
        """Return per-dimension scores plus the composite ACS."""
        m, c, d, x, i = self._structural_components(arch)
        h, n, v, e = self._codegen_components(source_dir)
        a, cc, dc, ic = self._constraint_components(problem)
        s = (_ALPHA[0]*m + _ALPHA[1]*c + _ALPHA[2]*d
             + _ALPHA[3]*x + _ALPHA[4]*i)
        g = _BETA[0]*h + _BETA[1]*n + _BETA[2]*v + _BETA[3]*e
        p = (_GAMMA[0]*a + _GAMMA[1]*cc + _GAMMA[2]*dc + _GAMMA[3]*ic)
        composite = _W[0]*s + _W[1]*g + _W[2]*p
        return ComplexityScore(
            structural=round(s, 2), codegen=round(g, 2),
            constraint=round(p, 2), composite=round(composite, 2),
            normalized=round(composite / _BASELINE, 3),
            components={"M": m, "C": c, "D": d, "X": x, "I": i,
                        "H": h, "N": n, "V": v, "E": e,
                        "A": a, "CC": cc, "DC": dc, "IC": ic},
        )

    @staticmethod
    def _structural_components(
        arch: ArchitectureSpec,
    ) -> tuple[int, int, int, int, int]:
        m = len(arch.modules)
        c = sum(len(mod.classes) for mod in arch.modules)
        d = sum(
            len(deps) for deps in arch.graph.edges.values()
        ) + sum(
            len(cls.depends) for mod in arch.modules for cls in mod.classes
        )
        x = sum(len(mod.exports) for mod in arch.modules)
        i = sum(len(mod.invariants) for mod in arch.modules) + sum(
            len(cls.invariants) for mod in arch.modules for cls in mod.classes
        )
        return m, c, d, x, i

    @staticmethod
    def _codegen_components(
        source_dir: Path | None,
    ) -> tuple[int, int, int, int]:
        if source_dir is None or not source_dir.is_dir():
            return 0, 0, 0, 0
        h = n = 0
        identifiers: set[str] = set()
        external_imports: set[str] = set()
        for py_file in source_dir.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text())
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            for node in ast.walk(tree):
                n += 1
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try,
                                     ast.With, ast.BoolOp, ast.AsyncFor)):
                    h += 1
                if isinstance(node, ast.Name):
                    identifiers.add(node.id)
                if isinstance(node, ast.ImportFrom) and node.module:
                    if not node.module.startswith(("src.", ".")):
                        external_imports.add(node.module.split(".")[0])
        return h, n, len(identifiers), len(external_imports)

    @staticmethod
    def _constraint_components(
        problem: ProblemSpec,
    ) -> tuple[int, int, int, int]:
        a = len(problem.acceptance_criteria)
        cc = len(problem.produces_contracts) + len(problem.consumes_contracts)
        dc = len(problem.data_classification)
        ic = len(problem.infrastructure_choices)
        return a, cc, dc, ic
