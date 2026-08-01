"""Compiled-target entries cover exactly Java / Go / Rust."""

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.testing.maven_test_runner import MavenTestRunner
from squeaky_clean.interface.cli.language_adapters.compiled_language_entries import (
    compiled_entries,
)


def test_covers_exactly_the_compiled_languages() -> None:
    assert set(compiled_entries()) == {
        TargetLanguage.JAVA,
        TargetLanguage.GO,
        TargetLanguage.RUST,
    }


def test_java_functional_exclude_uses_camel_case_glob() -> None:
    # Java test classes are *SecurityTest.java, not *security*.
    assert compiled_entries()[TargetLanguage.JAVA].functional_exclude == "*SecurityTest*"


def test_java_runner_factory_builds_maven_runner() -> None:
    runner = compiled_entries()[TargetLanguage.JAVA].runner_factory(None, None)
    assert isinstance(runner, MavenTestRunner)
