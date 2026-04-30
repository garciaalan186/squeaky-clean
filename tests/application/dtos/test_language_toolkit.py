"""Tests for LanguageToolkit DTO."""

import dataclasses

import pytest

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _python_toolkit() -> LanguageToolkit:
    return LanguageToolkit(
        language=TargetLanguage.PYTHON,
        file_extension=".py",
        test_file_prefix="test_",
        test_file_suffix=".py",
        icp_library="python",
        architect_library="python",
        identifier_case="snake",
    )


def test_language_toolkit_stores_all_fields() -> None:
    toolkit = _python_toolkit()
    assert toolkit.language is TargetLanguage.PYTHON
    assert toolkit.file_extension == ".py"
    assert toolkit.test_file_prefix == "test_"
    assert toolkit.icp_library == "python"
    assert toolkit.identifier_case == "snake"


def test_language_toolkit_is_frozen() -> None:
    toolkit = _python_toolkit()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(toolkit, "file_extension", ".js")  # noqa: B010
