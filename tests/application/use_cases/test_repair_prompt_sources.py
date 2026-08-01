"""Tests for RepairPromptSources (extracted from RepairTestFile)."""

from pathlib import Path

from squeaky_clean.application.generation.repair.repair_prompt_sources import (
    RepairPromptSources,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _project(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "calc.py").write_text("class Calc: ...\n")
    (tmp_path / "tests" / "test_calc.py").write_text("import pytest\n")
    (tmp_path / "tests" / "test_other.py").write_text("import unittest\n")
    return tmp_path


def test_sources_concatenates_production_files_only(tmp_path: Path) -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    text = RepairPromptSources().sources(_project(tmp_path), toolkit)
    assert "class Calc" in text
    assert "import pytest" not in text  # tests/ excluded


def test_exemplar_skips_the_file_under_repair(tmp_path: Path) -> None:
    project = _project(tmp_path)
    style = RepairPromptSources().exemplar(project, "tests/test_calc.py")
    assert style == "import unittest\n"


def test_exemplar_empty_when_no_other_test_exists(tmp_path: Path) -> None:
    project = _project(tmp_path)
    (project / "tests" / "test_other.py").unlink()
    assert RepairPromptSources().exemplar(project, "tests/test_calc.py") == ""
