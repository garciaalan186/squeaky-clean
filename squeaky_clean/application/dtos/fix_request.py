"""FixRequest DTO: inputs to FixFailingClasses.execute()."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult


@dataclass(frozen=True)
class FixRequest:
    """Bundle passed to FixFailingClasses for one fixer-stage invocation."""

    implementation: ModuleImplementation
    test_run_result: TestRunResult
    # When non-empty, these source-file stems drive the fix directly instead
    # of parsing them from test output — used by the compile gate, whose
    # compiler output is not in test-runner format.
    override_stems: tuple[str, ...] = ()
