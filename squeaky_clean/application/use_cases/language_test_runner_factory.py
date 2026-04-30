"""language_test_runner_factory: pick a TestRunner adapter for a target language."""

from __future__ import annotations

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.testing.cargo_test_runner import CargoTestRunner
from squeaky_clean.infrastructure.testing.go_test_runner import GoTestRunner
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.infrastructure.testing.node_test_runner import NodeTestRunner
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.infrastructure.testing.test_runner import TestRunner
from squeaky_clean.infrastructure.testing.typescript_test_runner import TypeScriptTestRunner


class LanguageTestRunnerFactory:
    """Returns the TestRunner subprocess adapter for a TargetLanguage."""

    def for_language(
        self, lang: TargetLanguage, exclude_glob: str | None = None,
    ) -> TestRunner:
        """Return the runner whose subprocess matches ``lang``."""
        if lang is TargetLanguage.PYTHON:
            return PytestRunner(exclude_glob=exclude_glob)
        if lang is TargetLanguage.JAVASCRIPT:
            return NodeTestRunner(exclude_glob=exclude_glob)
        if lang is TargetLanguage.TYPESCRIPT:
            return TypeScriptTestRunner(exclude_glob=exclude_glob)
        if lang is TargetLanguage.JAVA:
            return MavenTestRunner(exclude_glob=exclude_glob)
        if lang is TargetLanguage.GO:
            return GoTestRunner(exclude_glob=exclude_glob)
        if lang is TargetLanguage.RUST:
            return CargoTestRunner(exclude_glob=exclude_glob)
        raise ValueError(f"unsupported TargetLanguage: {lang}")
