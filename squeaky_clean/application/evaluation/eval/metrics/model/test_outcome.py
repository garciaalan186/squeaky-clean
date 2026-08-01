"""TestOutcome value object: pass rates and counts for one eval run (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestOutcome:
    """Immutable test-execution outcome for one eval run.

    ``test_status`` distinguishes a measured 0% pass rate from "no tests
    ran": "ok" (tests executed), "build_failed" (compile/collection
    errored before any test ran), "not_measured" (zero tests collected —
    toolchain absent). ``tests_collected`` is the executed test count
    backing it. ``tests_pass`` reflects functional acceptance criteria
    when a functional run exists (see RunEvalMetricsBuilder).
    """

    tests_pass: float = 0.0
    test_status: str = "ok"
    tests_collected: int = 0
    functional_test_count: int = 0
    functional_tests_pass: float = 0.0
    security_test_count: int = 0
    security_tests_pass: float = 0.0
