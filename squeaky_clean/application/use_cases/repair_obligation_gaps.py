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
        for rel, obs in self._group(gaps, request.output_dir).items():
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
        self, gaps: tuple[TestObligation, ...], output_dir: Path,
    ) -> dict[str, list[TestObligation]]:
        by_file: dict[str, list[TestObligation]] = {}
        for gap in gaps:
            rel = self._test_file_for(gap.target_class, output_dir)
            if rel is not None:
                by_file.setdefault(rel, []).append(gap)
        return by_file

    @staticmethod
    def _test_file_for(class_name: str, output_dir: Path) -> str | None:
        needle = re.compile(rf"\b{re.escape(class_name)}\b")
        for p in sorted(output_dir.rglob("*")):
            if not p.is_file() or not _TEST_FILE.search(p.name):
                continue
            if "node_modules" in p.parts or "target" in p.parts:
                continue
            try:
                if needle.search(p.read_text()):
                    return str(p.relative_to(output_dir))
            except OSError:
                continue
        return None

    @staticmethod
    def _instruction(obs: list[TestObligation]) -> str:
        lines = [
            "The generated test compiles but does NOT discharge these spec "
            "obligations. Add or strengthen a test for EACH so it exercises "
            "the behaviour and keeps a real assertion (never a trivial one):",
        ]
        for o in obs:
            detail = o.detail or "the declared outcome"
            lines.append(
                f"- from `{o.source}`: call {o.method} on {o.target_class} "
                f"and assert it {o.kind.value} ({detail})")
        return "\n".join(lines)

    @staticmethod
    def _empty() -> FixerStageResult:
        return FixerStageResult(0, 0, 0, 0.0, 0, 0)
