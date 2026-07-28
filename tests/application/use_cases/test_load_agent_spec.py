"""Tests for LoadAgentSpec."""

import pytest

from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec


def test_load_principal_architect_spec() -> None:
    text = LoadAgentSpec().load("RequirementCompiler")
    assert text.strip()
    assert "§Notation" in text
    assert "# Role: RequirementCompiler" in text


def test_load_unknown_spec_raises() -> None:
    with pytest.raises(FileNotFoundError):
        LoadAgentSpec().load("ThisDoesNotExist")


def test_load_go_entity_icp() -> None:
    text = LoadAgentSpec().load("go/ddd_clean/EntityEmitter")
    assert "# Role: EntityEmitter (Go)" in text
    assert "package main" in text


def test_load_go_strategy_icp() -> None:
    text = LoadAgentSpec().load("go/behavioral/StrategyEmitter")
    assert "# Role: StrategyEmitter (Go)" in text
    assert "interface" in text


def test_load_go_value_object_icp() -> None:
    text = LoadAgentSpec().load("go/ddd_clean/ValueObjectEmitter")
    assert "ValueObjectEmitter (Go)" in text


def test_load_go_simple_class_icp() -> None:
    text = LoadAgentSpec().load("go/ddd_clean/SimpleClassEmitter")
    assert "SimpleClassEmitter (Go)" in text


def test_load_go_test_architect() -> None:
    text = LoadAgentSpec().load("architects/go/OracleCompiler")
    assert "# Role: OracleCompiler (Go)" in text
    assert "_test.go" in text


def test_load_rust_entity_icp() -> None:
    text = LoadAgentSpec().load("rust/ddd_clean/EntityEmitter")
    assert "# Role: EntityEmitter (Rust)" in text
    assert "pub struct" in text


def test_load_rust_strategy_icp() -> None:
    text = LoadAgentSpec().load("rust/behavioral/StrategyEmitter")
    assert "# Role: StrategyEmitter (Rust)" in text
    assert "trait" in text


def test_load_rust_value_object_icp() -> None:
    text = LoadAgentSpec().load("rust/ddd_clean/ValueObjectEmitter")
    assert "ValueObjectEmitter (Rust)" in text


def test_load_rust_simple_class_icp() -> None:
    text = LoadAgentSpec().load("rust/ddd_clean/SimpleClassEmitter")
    assert "SimpleClassEmitter (Rust)" in text


def test_load_rust_test_architect() -> None:
    text = LoadAgentSpec().load("architects/rust/OracleCompiler")
    assert "# Role: OracleCompiler (Rust)" in text
    assert "#[cfg(test)]" in text
