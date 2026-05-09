"""K7: presence + non-stub check for Java/Go/Rust security ICP specs.

Today only Python has the 5 security-ICP variants. K7 ports them to
Java, Go, and Rust. This test asserts every (language, category) pair
has a non-stub spec file containing the language-specific idiom token.
"""

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ICPS_ROOT = _REPO_ROOT / "squeaky_clean" / "interface" / "agent_specs" / "icps"

_CATEGORIES = (
    "AccessControl",
    "Boundary",
    "ErrorSafety",
    "Injection",
    "InputValidation",
)

# Per-language idiom token that must appear inside the spec body. Its
# presence indicates the spec has been ported to the target language;
# its absence indicates a Python-syntax stub.
_LANGUAGE_TOKENS: dict[str, str] = {
    "java": "package com.example;",
    "go": "package main",
    "rust": "#[cfg(test)] mod tests",
}

_PARAMS = [
    (lang, cat) for lang in _LANGUAGE_TOKENS for cat in _CATEGORIES
]


@pytest.mark.parametrize(("language", "category"), _PARAMS)
def test_security_icp_spec_present_and_idiomatic(
    language: str, category: str,
) -> None:
    spec = _ICPS_ROOT / language / "security" / f"{category}SecurityICP.md"
    assert spec.is_file(), f"missing spec: {spec}"
    body = spec.read_text()
    token = _LANGUAGE_TOKENS[language]
    assert token in body, (
        f"{spec.name} appears to be a Python-syntax stub: "
        f"missing required token {token!r} for language {language!r}"
    )
