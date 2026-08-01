"""Tests for the LanguageAdapterBundle frozen DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.domain.interfaces.implemented_class_parser import ImplementedClassParser
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.interfaces.test_runner import TestRunner
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.interface.cli.language_adapter_bundle import LanguageAdapterBundle
from squeaky_clean.interface.cli.language_adapter_registry import REGISTRY


def _python_bundle() -> LanguageAdapterBundle:
    entry = REGISTRY[TargetLanguage.PYTHON]
    return LanguageAdapterBundle(
        test_runner=entry.runner_factory(None, None),
        functional_test_runner=entry.runner_factory(entry.functional_exclude, None),
        granularity_rule=entry.granularity_rule(),
        bootstrap=entry.bootstrap(LocalFileSystem()),
        parser=entry.parser(),
        dependency_installer=entry.installer(None),
    )


def test_every_field_satisfies_its_port() -> None:
    bundle = _python_bundle()
    assert isinstance(bundle.test_runner, TestRunner)
    assert isinstance(bundle.functional_test_runner, TestRunner)
    assert isinstance(bundle.granularity_rule, Rule)
    assert isinstance(bundle.bootstrap, IntegrationBootstrap)
    assert isinstance(bundle.parser, ImplementedClassParser)
    assert isinstance(bundle.dependency_installer, DependencyInstaller)


def test_functional_runner_is_a_distinct_instance() -> None:
    bundle = _python_bundle()
    assert bundle.functional_test_runner is not bundle.test_runner


def test_bundle_is_frozen() -> None:
    bundle = _python_bundle()
    with pytest.raises(FrozenInstanceError):
        bundle.parser = bundle.parser  # type: ignore[misc]
