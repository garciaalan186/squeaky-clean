"""Registry entries for the scripted targets (Python / JavaScript / TypeScript)."""

from __future__ import annotations

from squeaky_clean.application.generation.emission.parsers.javascript_implemented_class_parser import (
    JavaScriptImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)
from squeaky_clean.application.generation.integration.bootstrap.javascript_integration_bootstrap import (
    JavaScriptIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.typescript_integration_bootstrap import (
    TypeScriptIntegrationBootstrap,
)
from squeaky_clean.domain.rules.javascript_granularity_rule import JavaScriptGranularityRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.domain.rules.typescript_granularity_rule import TypeScriptGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.typescript_compiler import TypeScriptCompiler
from squeaky_clean.infrastructure.installers.npm_dependency_installer import (
    NpmDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.pip_dependency_installer import (
    PipDependencyInstaller,
)
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.infrastructure.testing.typescript_test_runner import TypeScriptTestRunner
from squeaky_clean.interface.cli.language_adapters.language_adapter_entry import (
    LanguageAdapterEntry,
)


def scripted_entries() -> dict[TargetLanguage, LanguageAdapterEntry]:
    """The interpreter-first languages (no ahead-of-time compile, TS aside)."""
    return {
        TargetLanguage.PYTHON: LanguageAdapterEntry(
            runner_factory=lambda glob, log: PytestRunner(exclude_glob=glob),
            functional_exclude="*security*",
            granularity_rule=PythonGranularityRule,
            bootstrap=PythonIntegrationBootstrap,
            parser=PythonImplementedClassParser,
            installer=PipDependencyInstaller,
        ),
        TargetLanguage.JAVASCRIPT: LanguageAdapterEntry(
            runner_factory=lambda glob, log: NodeTestRunner(exclude_glob=glob),
            functional_exclude="*security*",
            granularity_rule=JavaScriptGranularityRule,
            bootstrap=JavaScriptIntegrationBootstrap,
            parser=JavaScriptImplementedClassParser,
            installer=NpmDependencyInstaller,
        ),
        TargetLanguage.TYPESCRIPT: LanguageAdapterEntry(
            runner_factory=lambda glob, log: TypeScriptTestRunner(exclude_glob=glob),
            functional_exclude="*security*",
            granularity_rule=TypeScriptGranularityRule,
            bootstrap=TypeScriptIntegrationBootstrap,
            parser=JavaScriptImplementedClassParser,
            installer=NpmDependencyInstaller,
            compiler=TypeScriptCompiler,
        ),
    }
