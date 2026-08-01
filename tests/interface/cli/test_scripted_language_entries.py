"""Scripted-target entries cover exactly Python / JavaScript / TypeScript."""

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner
from squeaky_clean.interface.cli.language_adapters.scripted_language_entries import (
    scripted_entries,
)


def test_covers_exactly_the_scripted_languages() -> None:
    assert set(scripted_entries()) == {
        TargetLanguage.PYTHON,
        TargetLanguage.JAVASCRIPT,
        TargetLanguage.TYPESCRIPT,
    }


def test_only_typescript_declares_a_compiler() -> None:
    entries = scripted_entries()
    assert entries[TargetLanguage.TYPESCRIPT].compiler is not None
    assert entries[TargetLanguage.PYTHON].compiler is None
    assert entries[TargetLanguage.JAVASCRIPT].compiler is None


def test_python_runner_factory_builds_pytest_runner() -> None:
    runner = scripted_entries()[TargetLanguage.PYTHON].runner_factory(None, None)
    assert isinstance(runner, PytestRunner)
