"""TestRunResult DTO: parsed outcome of one test-runner subprocess run."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TestRunResult:
    """Immutable record of a single test-runner subprocess invocation.

    `passed`, `failed`, and `errors` are parsed from the runner's
    summary output. `duration_ms` is measured around the subprocess
    call. `raw_output` is the full stdout+stderr for diagnostic use
    in SUMMARY.md (first N lines excerpted if tests failed).
    """

    passed: int
    failed: int
    errors: int
    duration_ms: int
    raw_output: str
