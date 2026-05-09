"""Tests for PytestRunner."""

from pathlib import Path

from squeaky_clean.infrastructure.testing.pytest_runner import PytestRunner


def test_pytest_runner_runs_passing_test(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text("")
    (tmp_path / "tests" / "test_ok.py").write_text(
        "def test_ok() -> None:\n    assert 1 == 1\n"
    )
    result = PytestRunner().run(tmp_path)
    assert result.passed == 1
    assert result.failed == 0
    assert result.errors == 0


def test_pytest_runner_reports_failures(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text("")
    (tmp_path / "tests" / "test_bad.py").write_text(
        "def test_bad() -> None:\n    assert 1 == 2\n"
    )
    result = PytestRunner().run(tmp_path)
    assert result.passed == 0
    assert result.failed == 1


def test_pytest_runner_continues_on_collection_errors(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text("")
    (tmp_path / "tests" / "test_ok.py").write_text(
        "def test_ok() -> None:\n    assert 1 == 1\n"
    )
    (tmp_path / "tests" / "test_bad_import.py").write_text(
        "from nonexistent_module import FakeClass\n"
        "def test_impossible() -> None:\n    pass\n"
    )
    result = PytestRunner().run(tmp_path)
    assert result.passed == 1
    assert result.errors >= 1


def test_pytest_runner_exclude_glob_skips_files(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text("")
    (tmp_path / "tests" / "test_ok.py").write_text(
        "def test_ok() -> None:\n    assert 1 == 1\n"
    )
    (tmp_path / "tests" / "test_security_bad.py").write_text(
        "def test_sec() -> None:\n    assert 1 == 2\n"
    )
    result = PytestRunner(exclude_glob="*security*").run(tmp_path)
    assert result.passed == 1
    assert result.failed == 0
