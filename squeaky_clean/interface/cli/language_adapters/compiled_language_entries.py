"""Registry entries for the compiled targets (Java / Go / Rust)."""

from __future__ import annotations

from squeaky_clean.application.generation.emission.parsers.go_implemented_class_parser import (
    GoImplementedClassParser,
)
from squeaky_clean.application.generation.emission.parsers.java_implemented_class_parser import (
    JavaImplementedClassParser,
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
from squeaky_clean.application.generation.integration.bootstrap.rust_integration_bootstrap import (
    RustIntegrationBootstrap,
)
from squeaky_clean.domain.rules.go_granularity_rule import GoGranularityRule
from squeaky_clean.domain.rules.java_granularity_rule import JavaGranularityRule
from squeaky_clean.domain.rules.rust_granularity_rule import RustGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.java_compiler import JavaCompiler
from squeaky_clean.infrastructure.installers.cargo_dependency_installer import (
    CargoDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.go_dependency_installer import (
    GoDependencyInstaller,
)
from squeaky_clean.infrastructure.installers.maven_dependency_installer import (
    MavenDependencyInstaller,
)
from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner
from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.interface.cli.language_adapters.language_adapter_entry import (
    LanguageAdapterEntry,
)


def compiled_entries() -> dict[TargetLanguage, LanguageAdapterEntry]:
    """The ahead-of-time-compiled languages (loggers thread into their runners)."""
    return {
        TargetLanguage.JAVA: LanguageAdapterEntry(
            runner_factory=lambda glob, log: MavenTestRunner(exclude_glob=glob, logger=log),
            functional_exclude="*SecurityTest*",
            granularity_rule=JavaGranularityRule,
            bootstrap=JavaIntegrationBootstrap,
            parser=JavaImplementedClassParser,
            installer=MavenDependencyInstaller,
            compiler=JavaCompiler,
        ),
        TargetLanguage.GO: LanguageAdapterEntry(
            runner_factory=lambda glob, log: GoTestRunner(exclude_glob=glob, logger=log),
            functional_exclude="*security*",
            granularity_rule=GoGranularityRule,
            bootstrap=GoIntegrationBootstrap,
            parser=GoImplementedClassParser,
            installer=GoDependencyInstaller,
        ),
        TargetLanguage.RUST: LanguageAdapterEntry(
            runner_factory=lambda glob, log: CargoTestRunner(exclude_glob=glob, logger=log),
            functional_exclude="*security*",
            granularity_rule=RustGranularityRule,
            bootstrap=RustIntegrationBootstrap,
            parser=RustImplementedClassParser,
            installer=CargoDependencyInstaller,
        ),
    }
