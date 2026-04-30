"""FixRequest DTO: inputs to FixFailingClasses.execute()."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult


@dataclass(frozen=True)
class FixRequest:
    """Bundle passed to FixFailingClasses for one fixer-stage invocation."""

    implementation: ModuleImplementation
    test_run_result: TestRunResult
