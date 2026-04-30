"""TestRunner port: abstract interface for a per-language test subprocess runner."""

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult


class TestRunner(ABC):
    """Port for a subprocess-based test runner.

    Implementations shell out to the native test runner for the
    generated project's language (pytest for Python, node --test for
    JavaScript) and return a parsed TestRunResult. RunEvalPipeline
    invokes this once per problem and forwards the result to the
    metrics builder and report writer.
    """

    @abstractmethod
    def run(self, project_dir: Path) -> TestRunResult:
        """Run the test suite in ``project_dir`` and return a TestRunResult."""
