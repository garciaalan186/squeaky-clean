"""Tests for LanguageAdapterSelector."""

from squeaky_clean.application.use_cases.java_integration_bootstrap import (
    JavaIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.javascript_integration_bootstrap import (
    JavaScriptIntegrationBootstrap,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.domain.rules.java_granularity_rule import JavaGranularityRule
from squeaky_clean.domain.rules.javascript_granularity_rule import JavaScriptGranularityRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector


def test_python_adapter_bundle() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.test_runner, PytestRunner)
    assert isinstance(bundle.granularity_rule, PythonGranularityRule)
    assert isinstance(bundle.bootstrap, PythonIntegrationBootstrap)


def test_javascript_adapter_bundle() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVASCRIPT)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.test_runner, NodeTestRunner)
    assert isinstance(bundle.granularity_rule, JavaScriptGranularityRule)
    assert isinstance(bundle.bootstrap, JavaScriptIntegrationBootstrap)


def test_java_adapter_bundle() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.JAVA)
    bundle = LanguageAdapterSelector().select(toolkit, LocalFileSystem())
    assert isinstance(bundle.test_runner, MavenTestRunner)
    assert isinstance(bundle.granularity_rule, JavaGranularityRule)
    assert isinstance(bundle.bootstrap, JavaIntegrationBootstrap)
