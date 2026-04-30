"""Tests for TypeScriptTestRunner."""

from squeaky_clean.infrastructure.testing.typescript_test_runner import TypeScriptTestRunner


def test_typescript_test_runner_instantiates() -> None:
    runner = TypeScriptTestRunner()
    assert runner is not None
