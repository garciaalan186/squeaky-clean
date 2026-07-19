"""RepairObligationGaps: drive undischarged spec obligations to zero.

The convergence feedback edge. Compile/test fixing makes tests green; this
makes them FAITHFUL — a test can compile and pass while never exercising an
obligation the spec demands. Each pass locates the test file for a gapped
obligation and re-runs RepairTestFile with the obligation as an explicit
target, until no gaps remain or a pass makes no progress.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.test_obligation import TestObligation
from squeaky_clean.application.use_cases.check_test_obligations import (
    CheckTestObligations,
)
from squeaky_clean.application.use_cases.fixer_stage import FixerStageResult
from squeaky_clean.application.use_cases.repair_test_file import (
    RepairTestFile,
    TestRepairRequest,
)

_TEST_FILE = re.compile(r"(^test_.*\.py$|\.test\.(ts|js)$|Test\.java$)")


@dataclass(frozen=True)
class ObligationRepairRequest:
    """Inputs to one obligation-repair run."""

    obligations: tuple[TestObligation, ...]
    output_dir: Path
    toolkit: LanguageToolkit | None
    max_passes: int


@dataclass(frozen=True)
class ObligationRepairResult:
    """Residual undischarged obligations + aggregated repair usage."""

    residual_gaps: int
    usage: FixerStageResult


class RepairObligationGaps:
    """Repairs test files until they discharge the spec's obligations."""

    def __init__(self, repairer: RepairTestFile | None) -> None:
        self._repairer: RepairTestFile | None = repairer
        self._checker: CheckTestObligations = CheckTestObligations()

    def run(self, request: ObligationRepairRequest) -> ObligationRepairResult:
        """Repair up to ``max_passes`` times; return residual gaps + usage."""
        gaps = self._checker.check(request.obligations, request.output_dir)
        if self._repairer is None or request.toolkit is None:
            return ObligationRepairResult(len(gaps), self._empty())
        usage = self._empty()
        for _ in range(max(0, request.max_passes)):
            if not gaps:
                break
            stats = self._repair_pass(gaps, request)
            usage = usage.merge(stats)
            if stats.classes_fixed == 0:
                break
            gaps = self._checker.check(request.obligations, request.output_dir)
        return ObligationRepairResult(len(gaps), usage)

    def _repair_pass(
        self, gaps: tuple[TestObligation, ...],
        request: ObligationRepairRequest,
    ) -> FixerStageResult:
        repairer = self._repairer
        toolkit = request.toolkit
        if repairer is None or toolkit is None:
            return self._empty()
        n = 0
        cost = 0.0
        toks_in = toks_out = dur = 0
        for rel, obs in self._group(gaps, request).items():
            resp = repairer.repair(TestRepairRequest(
                request.output_dir, rel, self._instruction(obs), toolkit))
            if resp is None:
                continue
            n += 1
            cost += resp.cost_usd
            toks_in += resp.input_tokens
            toks_out += resp.output_tokens
            dur += resp.duration_ms
        return FixerStageResult(n, toks_in, toks_out, cost, dur, 1 if n else 0)

    def _group(
        self, gaps: tuple[TestObligation, ...],
        request: "ObligationRepairRequest",
    ) -> dict[str, list[TestObligation]]:
        by_file: dict[str, list[TestObligation]] = {}
        for gap in gaps:
            # Constructor-invariant duties go to a fresh dedicated file: the
            # repairer reliably CREATES a clean invariants test, whereas
            # asking it to graft an assertion into an existing storage-test
            # file is unreliable.
            rel = (self._invariants_path(gap.target_class, request.toolkit)
                   if gap.method == "<init>"
                   else self._test_file_for(gap.target_class, request))
            if rel is not None:
                by_file.setdefault(rel, []).append(gap)
        return by_file

    def _invariants_path(
        self, class_name: str, toolkit: LanguageToolkit | None,
    ) -> str | None:
        """Dedicated new test-file path for a class's invariant duties."""
        if toolkit is None:
            return None
        lang = toolkit.language.value
        if lang == "python":
            return f"tests/test_{self._snake(class_name)}_invariants.py"
        if lang in ("typescript", "javascript"):
            ext = "ts" if lang == "typescript" else "js"
            return f"tests/{self._camel(class_name)}Invariants.test.{ext}"
        if lang == "java":
            return f"src/test/java/com/example/{class_name}InvariantsTest.java"
        return None

    def _test_file_for(
        self, class_name: str, request: "ObligationRepairRequest",
    ) -> str | None:
        """The class's own test file — an existing one, else a new path.

        Prefers a test file whose stem is the class name; falls back to any
        test that references it; when none exists, returns a canonical new
        path so the repairer CREATES the missing test.
        """
        forms = self._forms(class_name)
        named: str | None = None
        mentions: str | None = None
        for p in sorted(request.output_dir.rglob("*")):
            if (not p.is_file() or not _TEST_FILE.search(p.name)
                    or "node_modules" in p.parts or "target" in p.parts):
                continue
            stem = p.name.split(".")[0].replace("Test", "")
            rel = str(p.relative_to(request.output_dir))
            if stem in forms and named is None:
                named = rel
            elif mentions is None and re.search(
                    rf"\b{re.escape(class_name)}\b", self._read(p)):
                mentions = rel
        return named or mentions or self._canonical(class_name, request.toolkit)

    @staticmethod
    def _read(path: Path) -> str:
        try:
            return path.read_text()
        except OSError:
            return ""

    def _canonical(
        self, class_name: str, toolkit: LanguageToolkit | None,
    ) -> str | None:
        """Canonical new test path for a class with no test file yet."""
        if toolkit is None:
            return None
        lang = toolkit.language.value
        if lang == "python":
            return f"tests/test_{self._snake(class_name)}.py"
        if lang in ("typescript", "javascript"):
            ext = "ts" if lang == "typescript" else "js"
            return f"tests/{self._camel(class_name)}.test.{ext}"
        if lang == "java":
            return f"src/test/java/com/example/{class_name}Test.java"
        return None

    def _forms(self, name: str) -> set[str]:
        return {name, self._snake(name), self._camel(name)}

    @staticmethod
    def _snake(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def _camel(self, name: str) -> str:
        parts = [p for p in self._snake(name).split("_") if p]
        return parts[0] + "".join(p.title() for p in parts[1:]) if parts else name

    @staticmethod
    def _instruction(obs: list[TestObligation]) -> str:
        lines = [
            "The generated test compiles but does NOT discharge these spec "
            "obligations. Add or strengthen a test for EACH so it exercises "
            "the behaviour and keeps a real assertion (never a trivial one):",
        ]
        for o in obs:
            if o.method == "<init>":
                lines.append(
                    f"- from `{o.source}`: construct {o.target_class} with "
                    f"input that VIOLATES \"{o.detail}\" and assert the "
                    f"constructor raises")
            else:
                detail = o.detail or "the declared outcome"
                lines.append(
                    f"- from `{o.source}`: call {o.method} on {o.target_class} "
                    f"and assert it {o.kind.value} ({detail})")
        return "\n".join(lines)

    @staticmethod
    def _empty() -> FixerStageResult:
        return FixerStageResult(0, 0, 0, 0.0, 0, 0)
