"""LanguageAdapterRegistry: registry-driven dispatch for per-language bundles."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from squeaky_clean.application.use_cases.go_integration_bootstrap import (
    GoIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.java_integration_bootstrap import (
    JavaIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.javascript_integration_bootstrap import (
    JavaScriptIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.parsers.go_implemented_class_parser import (
    GoImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.java_implemented_class_parser import (
    JavaImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.javascript_implemented_class_parser import (
    JavaScriptImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)
from squeaky_clean.application.use_cases.parsers.rust_implemented_class_parser import (
    RustImplementedClassParser,
)
from squeaky_clean.application.use_cases.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.rust_integration_bootstrap import (
    RustIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.typescript_integration_bootstrap import (
    TypeScriptIntegrationBootstrap,
)
from squeaky_clean.domain.interfaces.implemented_class_parser import (
    ImplementedClassParser,
)
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.rules.go_granularity_rule import GoGranularityRule
from squeaky_clean.domain.rules.java_granularity_rule import JavaGranularityRule
from squeaky_clean.domain.rules.javascript_granularity_rule import JavaScriptGranularityRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.domain.rules.rust_granularity_rule import RustGranularityRule
from squeaky_clean.domain.rules.typescript_granularity_rule import TypeScriptGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner
from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.infrastructure.testing.test_runner import TestRunner
from squeaky_clean.infrastructure.testing.typescript_test_runner import TypeScriptTestRunner


@dataclass(frozen=True)
class LanguageAdapterEntry:
    """Per-language factories for the runtime adapters."""

    runner: Callable[[], TestRunner]
    functional_runner: Callable[[], TestRunner]
    granularity_rule: Callable[[], Rule]
    bootstrap: Callable[[ProjectFileSystem], IntegrationBootstrap]
    parser: Callable[[], ImplementedClassParser]


REGISTRY: dict[TargetLanguage, LanguageAdapterEntry] = {
    TargetLanguage.PYTHON: LanguageAdapterEntry(
        runner=PytestRunner,
        functional_runner=lambda: PytestRunner(exclude_glob="*security*"),
        granularity_rule=PythonGranularityRule,
        bootstrap=PythonIntegrationBootstrap,
        parser=PythonImplementedClassParser,
    ),
    TargetLanguage.JAVASCRIPT: LanguageAdapterEntry(
        runner=NodeTestRunner,
        functional_runner=lambda: NodeTestRunner(exclude_glob="*security*"),
        granularity_rule=JavaScriptGranularityRule,
        bootstrap=JavaScriptIntegrationBootstrap,
        parser=JavaScriptImplementedClassParser,
    ),
    TargetLanguage.TYPESCRIPT: LanguageAdapterEntry(
        runner=TypeScriptTestRunner,
        functional_runner=lambda: TypeScriptTestRunner(exclude_glob="*security*"),
        granularity_rule=TypeScriptGranularityRule,
        bootstrap=TypeScriptIntegrationBootstrap,
        parser=JavaScriptImplementedClassParser,
    ),
    TargetLanguage.JAVA: LanguageAdapterEntry(
        runner=MavenTestRunner,
        functional_runner=lambda: MavenTestRunner(exclude_glob="*SecurityTest*"),
        granularity_rule=JavaGranularityRule,
        bootstrap=JavaIntegrationBootstrap,
        parser=JavaImplementedClassParser,
    ),
    TargetLanguage.GO: LanguageAdapterEntry(
        runner=GoTestRunner,
        functional_runner=lambda: GoTestRunner(exclude_glob="*security*"),
        granularity_rule=GoGranularityRule,
        bootstrap=GoIntegrationBootstrap,
        parser=GoImplementedClassParser,
    ),
    TargetLanguage.RUST: LanguageAdapterEntry(
        runner=CargoTestRunner,
        functional_runner=lambda: CargoTestRunner(exclude_glob="*security*"),
        granularity_rule=RustGranularityRule,
        bootstrap=RustIntegrationBootstrap,
        parser=RustImplementedClassParser,
    ),
}
