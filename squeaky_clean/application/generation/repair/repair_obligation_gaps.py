"""RepairObligationGaps: drive undischarged spec obligations to zero.

The convergence feedback edge: compile/test fixing makes tests green; this
makes them FAITHFUL. Each pass locates the test file for a gapped obligation
and re-runs RepairTestFile against it until no gaps remain or no progress.
"""

from squeaky_clean.application.generation.repair.fixer_stage import FixerStageResult
from squeaky_clean.application.generation.repair.obligations.obligation_instruction import (
    build_instruction,
)
from squeaky_clean.application.generation.repair.obligations.obligation_repair_request import (
    ObligationRepairRequest as ObligationRepairRequest,  # re-export: staged split (R6.11)
)
from squeaky_clean.application.generation.repair.obligations.obligation_repair_result import (
    ObligationRepairResult,
)
from squeaky_clean.application.generation.repair.obligations.obligation_test_file_locator import (
    ObligationTestFileLocator,
)
from squeaky_clean.application.generation.repair.repair_test_file import (
    RepairTestFile,
    TestRepairRequest,
)
from squeaky_clean.application.generation.testgen.check_test_obligations import (
    CheckTestObligations,
)
from squeaky_clean.application.generation.testgen.test_obligation import TestObligation


class RepairObligationGaps:
    """Repairs test files until they discharge the spec's obligations."""

    def __init__(self, repairer: RepairTestFile | None) -> None:
        self._repairer: RepairTestFile | None = repairer
        self._checker: CheckTestObligations = CheckTestObligations()
        self._locator: ObligationTestFileLocator = ObligationTestFileLocator()

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
        for rel, obs in self._locator.group(gaps, request).items():
            resp = repairer.repair(TestRepairRequest(
                request.output_dir, rel, build_instruction(obs), toolkit))
            if resp is None:
                continue
            n += 1
            cost += resp.cost_usd
            toks_in += resp.input_tokens
            toks_out += resp.output_tokens
            dur += resp.duration_ms
        return FixerStageResult(n, toks_in, toks_out, cost, dur, 1 if n else 0)

    @staticmethod
    def _empty() -> FixerStageResult:
        return FixerStageResult(0, 0, 0, 0.0, 0, 0)
