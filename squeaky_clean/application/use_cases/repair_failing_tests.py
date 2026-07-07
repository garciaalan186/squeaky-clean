"""RepairFailingTests: repair a test that CRASHES (not a real assertion).

Languages with a compile gate get their test files repaired on compile
failure; a Python test has no such gate, so a hallucinated line (e.g.
``blob.store.count`` on a dict) fails only at runtime and is never fixed.
This repairs test files whose failure is a test-code crash — AttributeError,
TypeError, NameError, and the like — while deliberately leaving plain
AssertionError alone, because a failed assertion may be a real source bug
that must not be silently rewritten away.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.fixer_stage import FixerStageResult
from squeaky_clean.application.use_cases.repair_test_file import (
    RepairTestFile,
    TestRepairRequest,
)

# "<path>:<line>: <ErrorType>" — pytest/traceback error-location line.
_LOC = re.compile(r"^(\S+?\.(?:py|ts|js|java)):\d+: (\w*(?:Error|Exception))",
                  re.MULTILINE)
# A failed assertion may signal a real source bug — never rewrite it away.
_ASSERTION = frozenset({"AssertionError"})


@dataclass(frozen=True)
class FailingTestsRequest:
    """Inputs to one failing-test repair pass."""

    raw_output: str
    output_dir: Path
    toolkit: LanguageToolkit | None


def _is_test_file(name: str) -> bool:
    return (name.startswith("test_") and name.endswith(".py")) \
        or name.endswith((".test.ts", ".test.js")) \
        or name.endswith("Test.java")


class RepairFailingTests:
    """Repairs test files that crash at runtime (never a bare assertion)."""

    def __init__(self, repairer: RepairTestFile | None) -> None:
        self._repairer: RepairTestFile | None = repairer

    def run(self, request: FailingTestsRequest) -> FixerStageResult:
        """Repair each crashing test file; return aggregated usage."""
        repairer = self._repairer
        toolkit = request.toolkit
        if repairer is None or toolkit is None:
            return self._empty()
        n = 0
        cost = 0.0
        toks_in = toks_out = dur = 0
        for rel in self._crashing_tests(request):
            resp = repairer.repair(TestRepairRequest(
                request.output_dir, rel,
                f"This test CRASHES at runtime (not a real assertion "
                f"failure). Fix the test's own bug against the source:\n"
                f"{request.raw_output[:2500]}", toolkit))
            if resp is None:
                continue
            n += 1
            cost += resp.cost_usd
            toks_in += resp.input_tokens
            toks_out += resp.output_tokens
            dur += resp.duration_ms
        return FixerStageResult(n, toks_in, toks_out, cost, dur, 1 if n else 0)

    def _crashing_tests(self, request: FailingTestsRequest) -> list[str]:
        seen: list[str] = []
        for path, err in _LOC.findall(request.raw_output):
            if err in _ASSERTION:
                continue
            name = path.rsplit("/", 1)[-1]
            if not _is_test_file(name):
                continue
            if path not in seen and (request.output_dir / path).is_file():
                seen.append(path)
        return seen

    @staticmethod
    def _empty() -> FixerStageResult:
        return FixerStageResult(0, 0, 0, 0.0, 0, 0)
