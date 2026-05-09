"""Parametrized test: every TargetLanguage produces a non-None installer."""

import pytest

from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
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
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector

_EXPECTED: dict[TargetLanguage, type[DependencyInstaller]] = {
    TargetLanguage.PYTHON: PipDependencyInstaller,
    TargetLanguage.JAVASCRIPT: NpmDependencyInstaller,
    TargetLanguage.TYPESCRIPT: NpmDependencyInstaller,
    TargetLanguage.JAVA: MavenDependencyInstaller,
    TargetLanguage.GO: GoDependencyInstaller,
    TargetLanguage.RUST: CargoDependencyInstaller,
}


@pytest.mark.parametrize("language", list(TargetLanguage))
def test_every_language_returns_non_none_installer(
    language: TargetLanguage,
) -> None:
    toolkit = LanguageToolkitFactory().for_language(language)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert bundle.dependency_installer is not None
    assert isinstance(bundle.dependency_installer, _EXPECTED[language])
