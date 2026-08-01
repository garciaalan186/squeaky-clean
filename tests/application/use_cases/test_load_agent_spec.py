"""Tests for LoadAgentSpec."""

import pytest

from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec


def test_load_principal_architect_spec() -> None:
    text = LoadAgentSpec().load("RequirementCompiler")
    assert text.strip()
    assert "§Notation" in text
    assert "# Role: RequirementCompiler" in text


def test_load_unknown_spec_raises() -> None:
    with pytest.raises(FileNotFoundError):
        LoadAgentSpec().load("ThisDoesNotExist")


# R6.10: Go/Rust emitter fleets are archived under agent_specs/_attic/
# emitters/ (out of the loader search path) until a real problem funds
# them. Loading one must now fail loudly rather than resolve silently.
def test_archived_go_emitter_spec_is_off_the_loader_path() -> None:
    with pytest.raises(FileNotFoundError):
        LoadAgentSpec().load("go/ddd_clean/EntityEmitter")


def test_archived_rust_emitter_spec_is_off_the_loader_path() -> None:
    with pytest.raises(FileNotFoundError):
        LoadAgentSpec().load("rust/ddd_clean/EntityEmitter")


def test_load_go_test_architect() -> None:
    text = LoadAgentSpec().load("architects/go/OracleCompiler")
    assert "# Role: OracleCompiler (Go)" in text
    assert "_test.go" in text


def test_load_rust_test_architect() -> None:
    text = LoadAgentSpec().load("architects/rust/OracleCompiler")
    assert "# Role: OracleCompiler (Rust)" in text
    assert "#[cfg(test)]" in text
