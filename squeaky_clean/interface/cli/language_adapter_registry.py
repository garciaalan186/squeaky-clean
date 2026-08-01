"""LanguageAdapterRegistry: the ONE per-language dispatch table (R6.7).

Every per-language constructor lives here — test runners, granularity
rules, integration bootstraps, class parsers, dependency installers and
(optional) ahead-of-time compilers. The selector / compiler-factory /
test-runner-factory modules are thin views over this table.

Go/Rust stay registered: R6.10 archived their EMITTER SPEC fleets (see
ACTIVE_EMITTER_LANGUAGES in map_pattern_to_emitter), not their toolchain
adapters — a recovered/replayed Go or Rust run must still dispatch.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from squeaky_clean.application.generation.emission.parsers.go_implemented_class_parser import (
    GoImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.java_implemented_class_parser import (
    JavaImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.javascript_implemented_class_parser import (
    JavaScriptImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.rust_implemented_class_parser import (
    RustImplementedClassParser,
)
from squeaky_clean.application.generation.integration.bootstrap.go_integration_bootstrap import (
    GoIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.java_integration_bootstrap import (
    JavaIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.javascript_integration_bootstrap import (
    JavaScriptIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.rust_integration_bootstrap import (
    RustIntegrationBootstrap,
)
from squeaky_clean.application.generation.integration.bootstrap.typescript_integration_bootstrap import (
    TypeScriptIntegrationBootstrap,
)
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.implemented_class_parser import (
    ImplementedClassParser,
)
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.interfaces.test_runner import TestRunner
from squeaky_clean.domain.rules.go_granularity_rule import GoGranularityRule
from squeaky_clean.domain.rules.java_granularity_rule import JavaGranularityRule
from squeaky_clean.domain.rules.javascript_granularity_rule import JavaScriptGranularityRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.domain.rules.rust_granularity_rule import RustGranularityRule
from squeaky_clean.domain.rules.typescript_granularity_rule import TypeScriptGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.java_compiler import JavaCompiler
from squeaky_clean.infrastructure.compilation.typescript_compiler import TypeScriptCompiler
from squeaky_clean.infrastructure.installers.cargo_dependency_installer import (
    CargoDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.go_dependency_installer import (
    GoDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.maven_dependency_installer import (
    MavenDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.npm_dependency_installer import (
    NpmDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.pip_dependency_installer import (
    PipDependencyInstaller,
)
from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner
from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.infrastructure.testing.typescript_test_runner import TypeScriptTestRunner


@dataclass(frozen=True)
class LanguageAdapterEntry:
    """Per-language factories for every runtime adapter.

    ``runner_factory`` takes an exclude glob (None = run everything), so a
    single field serves the plain runner, the functional runner (paired with
    ``functional_exclude``) and LanguageTestRunnerFactory's arbitrary-glob
    lookups — the mapping is never restated. ``compiler`` is None for
    languages without a meaningful ahead-of-time compile/typecheck step.
    """

    runner_factory: Callable[[str | None], TestRunner]
    functional_exclude: str
    granularity_rule: Callable[[], Rule]
    bootstrap: Callable[[ProjectFileSystem], IntegrationBootstrap]
    parser: Callable[[], ImplementedClassParser]
    installer: Callable[[], DependencyInstaller]
    compiler: Callable[[], ProjectCompiler] | None = None


REGISTRY: dict[TargetLanguage, LanguageAdapterEntry] = {
    TargetLanguage.PYTHON: LanguageAdapterEntry(
        runner_factory=lambda glob: PytestRunner(exclude_glob=glob),
        functional_exclude="*security*",
        granularity_rule=PythonGranularityRule,
        bootstrap=PythonIntegrationBootstrap,
        parser=PythonImplementedClassParser,
        installer=PipDependencyInstaller,
    ),
    TargetLanguage.JAVASCRIPT: LanguageAdapterEntry(
        runner_factory=lambda glob: NodeTestRunner(exclude_glob=glob),
        functional_exclude="*security*",
        granularity_rule=JavaScriptGranularityRule,
        bootstrap=JavaScriptIntegrationBootstrap,
        parser=JavaScriptImplementedClassParser,
        installer=NpmDependencyInstaller,
    ),
    TargetLanguage.TYPESCRIPT: LanguageAdapterEntry(
        runner_factory=lambda glob: TypeScriptTestRunner(exclude_glob=glob),
        functional_exclude="*security*",
        granularity_rule=TypeScriptGranularityRule,
        bootstrap=TypeScriptIntegrationBootstrap,
        parser=JavaScriptImplementedClassParser,
        installer=NpmDependencyInstaller,
        compiler=TypeScriptCompiler,
    ),
    TargetLanguage.JAVA: LanguageAdapterEntry(
        runner_factory=lambda glob: MavenTestRunner(exclude_glob=glob),
        functional_exclude="*SecurityTest*",
        granularity_rule=JavaGranularityRule,
        bootstrap=JavaIntegrationBootstrap,
        parser=JavaImplementedClassParser,
        installer=MavenDependencyInstaller,
        compiler=JavaCompiler,
    ),
    TargetLanguage.GO: LanguageAdapterEntry(
        runner_factory=lambda glob: GoTestRunner(exclude_glob=glob),
        functional_exclude="*security*",
        granularity_rule=GoGranularityRule,
        bootstrap=GoIntegrationBootstrap,
        parser=GoImplementedClassParser,
        installer=GoDependencyInstaller,
    ),
    TargetLanguage.RUST: LanguageAdapterEntry(
        runner_factory=lambda glob: CargoTestRunner(exclude_glob=glob),
        functional_exclude="*security*",
        granularity_rule=RustGranularityRule,
        bootstrap=RustIntegrationBootstrap,
        parser=RustImplementedClassParser,
        installer=CargoDependencyInstaller,
    ),
}
