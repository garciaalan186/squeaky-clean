"""LanguageAdapterSelector: registry-driven dispatch for per-language bundles."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
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
from squeaky_clean.interface.cli.language_adapter_bundle import LanguageAdapterBundle
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY

_INSTALLERS: dict[TargetLanguage, type[DependencyInstaller]] = {
    TargetLanguage.PYTHON: PipDependencyInstaller,
    TargetLanguage.JAVASCRIPT: NpmDependencyInstaller,
    TargetLanguage.TYPESCRIPT: NpmDependencyInstaller,
    TargetLanguage.JAVA: MavenDependencyInstaller,
    TargetLanguage.GO: GoDependencyInstaller,
    TargetLanguage.RUST: CargoDependencyInstaller,
}


class LanguageAdapterSelector:
    """Selects the test runner / granularity rule / bootstrap for a toolkit."""

    def select(
        self, toolkit: LanguageToolkit, fs: ProjectFileSystem,
    ) -> LanguageAdapterBundle:
        """Return the adapter bundle matching ``toolkit.language``."""
        entry = REGISTRY.get(toolkit.language)
        installer_cls = _INSTALLERS.get(toolkit.language)
        if entry is None or installer_cls is None:
            raise ValueError(f"unsupported TargetLanguage: {toolkit.language}")
        return LanguageAdapterBundle(
            test_runner=entry.runner(),
            functional_test_runner=entry.functional_runner(),
            granularity_rule=entry.granularity_rule(),
            bootstrap=entry.bootstrap(fs),
            parser=entry.parser(),
            dependency_installer=installer_cls(),
        )
