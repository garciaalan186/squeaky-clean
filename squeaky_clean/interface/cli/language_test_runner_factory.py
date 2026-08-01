"""language_test_runner_factory: runner view over the LanguageAdapterRegistry (R6.7)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.interfaces.test_runner import TestRunner
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY


class LanguageTestRunnerFactory:
    """Returns the TestRunner subprocess adapter for a TargetLanguage."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._logger: RunLogger = logger or NullRunLogger()

    def for_language(
        self, lang: TargetLanguage, exclude_glob: str | None = None,
    ) -> TestRunner:
        """Return the runner whose subprocess matches ``lang``."""
        entry = REGISTRY.get(lang)
        if entry is None:
            raise ValueError(f"unsupported TargetLanguage: {lang}")
        return entry.runner_factory(exclude_glob, self._logger)
