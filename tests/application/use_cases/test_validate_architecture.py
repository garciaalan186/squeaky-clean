"""Tests for ValidateArchitecture."""

from pathlib import Path

from squeaky_clean.application.use_cases.rule_runner import RuleRunner
from squeaky_clean.application.use_cases.validate_architecture import ValidateArchitecture
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule


def test_validate_architecture_reports_violations(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("class Foo:\n    pass\n")
    long_body = "\n".join(f"# line {i}" for i in range(90))
    (tmp_path / "long.py").write_text(long_body)
    rules: tuple[Rule, ...] = (PythonGranularityRule(),)
    uc = ValidateArchitecture(RuleRunner(rules))
    report = uc.execute(tmp_path)
    assert report.is_valid is False
    assert report.files_scanned == 2
    assert any("lines" in v.message for v in report.violations)


def test_validate_architecture_clean_project(tmp_path: Path) -> None:
    (tmp_path / "clean.py").write_text("class Foo:\n    pass\n")
    rules: tuple[Rule, ...] = (PythonGranularityRule(),)
    uc = ValidateArchitecture(RuleRunner(rules))
    report = uc.execute(tmp_path)
    assert report.is_valid is True
    assert report.files_scanned == 1
