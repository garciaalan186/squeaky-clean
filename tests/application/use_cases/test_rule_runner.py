"""Tests for RuleRunner."""

from pathlib import Path

from squeaky_clean.application.use_cases.rule_runner import RuleRunner
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.rules.dependency_rule import DependencyRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule


def test_rule_runner_aggregates_violations_across_files(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("class Foo:\n    pass\n")
    long_body = "\n".join(f"# line {i}" for i in range(90))
    (tmp_path / "long.py").write_text(long_body)
    rules: tuple[Rule, ...] = (PythonGranularityRule(), DependencyRule())
    runner = RuleRunner(rules)
    violations = runner.run(tmp_path)
    assert any("lines" in v.message for v in violations)
    assert all(v.rule_name == "PythonGranularityRule" for v in violations)


def test_rule_runner_returns_empty_when_dir_missing(tmp_path: Path) -> None:
    runner = RuleRunner((PythonGranularityRule(),))
    assert runner.run(tmp_path / "missing") == ()
