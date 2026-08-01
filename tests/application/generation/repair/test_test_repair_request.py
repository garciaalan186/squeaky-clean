"""Tests for the TestRepairRequest DTO."""

from pathlib import Path

import pytest

from squeaky_clean.application.generation.repair.test_repair_request import (
    TestRepairRequest,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def test_holds_repair_inputs() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    req = TestRepairRequest(
        project_dir=Path("/tmp/proj"), rel_path="tests/test_calc.py",
        error_excerpt="NameError: Calc", toolkit=toolkit,
    )
    assert req.rel_path == "tests/test_calc.py"
    assert req.toolkit is toolkit


def test_is_frozen() -> None:
    toolkit = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)
    req = TestRepairRequest(
        project_dir=Path("."), rel_path="t.py", error_excerpt="", toolkit=toolkit,
    )
    with pytest.raises(AttributeError):
        req.rel_path = "other.py"  # type: ignore[misc]
