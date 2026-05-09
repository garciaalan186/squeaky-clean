"""LanguageAdapterBundle DTO: swappable per-language adapters for DependencyBuilder."""

from dataclasses import dataclass

from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.implemented_class_parser import ImplementedClassParser
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.infrastructure.testing.test_runner import TestRunner


@dataclass(frozen=True)
class LanguageAdapterBundle:
    """Immutable bundle of swappable adapters that vary per target language.

    Bundling these lets ``DependencyBuilder`` stay within the
    <=2-args rule while still picking a TestRunner, a granularity
    Rule, an IntegrationBootstrap, a class parser, and a dependency
    installer per ``LanguageToolkit``.
    """

    test_runner: TestRunner
    functional_test_runner: TestRunner
    granularity_rule: Rule
    bootstrap: IntegrationBootstrap
    parser: ImplementedClassParser
    dependency_installer: DependencyInstaller
