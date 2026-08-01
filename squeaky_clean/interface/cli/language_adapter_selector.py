"""LanguageAdapterSelector: bundle view over the LanguageAdapterRegistry (R6.7)."""

from collections.abc import Callable

from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.language_adapter_bundle import LanguageAdapterBundle
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY

# Derived view kept for callers/tests; the registry is the single source.
_INSTALLERS: dict[TargetLanguage, Callable[[RunLogger | None], DependencyInstaller]] = {
    language: entry.installer for language, entry in REGISTRY.items()
}


class LanguageAdapterSelector:
    """Selects the test runner / granularity rule / bootstrap for a toolkit.

    R6.4b: the composition root passes its run logger so subprocess
    adapters (test runners, installers) report loudly; unwired they
    default to the silent ``NullRunLogger``.
    """

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._logger: RunLogger = logger or NullRunLogger()

    def select(
        self, toolkit: LanguageToolkit, fs: ProjectFileSystem,
    ) -> LanguageAdapterBundle:
        """Return the adapter bundle matching ``toolkit.language``."""
        entry = REGISTRY.get(toolkit.language)
        if entry is None:
            raise ValueError(f"unsupported TargetLanguage: {toolkit.language}")
        log = self._logger
        return LanguageAdapterBundle(
            test_runner=entry.runner_factory(None, log),
            functional_test_runner=entry.runner_factory(
                entry.functional_exclude, log,
            ),
            granularity_rule=entry.granularity_rule(),
            bootstrap=entry.bootstrap(fs),
            parser=entry.parser(),
            dependency_installer=entry.installer(log),
        )
