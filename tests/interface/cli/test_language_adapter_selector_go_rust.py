"""Tests: LanguageAdapterSelector returns correct bundles for Go and Rust."""

from squeaky_clean.application.use_cases.go_integration_bootstrap import (
    GoIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.rust_integration_bootstrap import (
    RustIntegrationBootstrap,
)
from squeaky_clean.domain.rules.go_granularity_rule import GoGranularityRule
from squeaky_clean.domain.rules.rust_granularity_rule import RustGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner
from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector


def test_go_toolkit_returns_go_bundle() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.GO)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.test_runner, GoTestRunner)
    assert isinstance(bundle.functional_test_runner, GoTestRunner)
    assert isinstance(bundle.granularity_rule, GoGranularityRule)
    assert isinstance(bundle.bootstrap, GoIntegrationBootstrap)


def test_rust_toolkit_returns_rust_bundle() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.RUST)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.test_runner, CargoTestRunner)
    assert isinstance(bundle.functional_test_runner, CargoTestRunner)
    assert isinstance(bundle.granularity_rule, RustGranularityRule)
    assert isinstance(bundle.bootstrap, RustIntegrationBootstrap)
