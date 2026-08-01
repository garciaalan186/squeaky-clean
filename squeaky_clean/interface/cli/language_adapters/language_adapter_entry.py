"""LanguageAdapterEntry: per-language factory bundle for the R6.7 registry."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.implemented_class_parser import (
    ImplementedClassParser,
)
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.interfaces.test_runner import TestRunner


@dataclass(frozen=True)
class LanguageAdapterEntry:
    """Per-language factories for every runtime adapter.

    ``runner_factory`` takes an exclude glob (None = run everything) plus
    the composition root's RunLogger (None = silent, R6.4b), so a
    single field serves the plain runner, the functional runner (paired with
    ``functional_exclude``) and LanguageTestRunnerFactory's arbitrary-glob
    lookups — the mapping is never restated. ``compiler`` is None for
    languages without a meaningful ahead-of-time compile/typecheck step.
    """

    runner_factory: Callable[[str | None, RunLogger | None], TestRunner]
    functional_exclude: str
    granularity_rule: Callable[[], Rule]
    bootstrap: Callable[[ProjectFileSystem], IntegrationBootstrap]
    parser: Callable[[], ImplementedClassParser]
    installer: Callable[[RunLogger | None], DependencyInstaller]
    compiler: Callable[[], ProjectCompiler] | None = None
