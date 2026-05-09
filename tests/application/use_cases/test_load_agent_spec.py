"""Tests for LoadAgentSpec."""

import pytest

from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec


def test_load_principal_architect_spec() -> None:
    text = LoadAgentSpec().load("PrincipalArchitect")
    assert text.strip()
    assert "§Notation" in text
    assert "# Role: PrincipalArchitect" in text


def test_load_unknown_spec_raises() -> None:
    with pytest.raises(FileNotFoundError):
        LoadAgentSpec().load("ThisDoesNotExist")


def test_load_go_entity_icp() -> None:
    text = LoadAgentSpec().load("icps/go/ddd_clean/EntityICP")
    assert "# Role: EntityICP (Go)" in text
    assert "package main" in text


def test_load_go_strategy_icp() -> None:
    text = LoadAgentSpec().load("icps/go/behavioral/StrategyICP")
    assert "# Role: StrategyICP (Go)" in text
    assert "interface" in text


def test_load_go_value_object_icp() -> None:
    text = LoadAgentSpec().load("icps/go/ddd_clean/ValueObjectICP")
    assert "ValueObjectICP (Go)" in text


def test_load_go_simple_class_icp() -> None:
    text = LoadAgentSpec().load("icps/go/ddd_clean/SimpleClassICP")
    assert "SimpleClassICP (Go)" in text


def test_load_go_test_architect() -> None:
    text = LoadAgentSpec().load("architects/go/TestArchitect")
    assert "# Role: TestArchitect (Go)" in text
    assert "_test.go" in text


def test_load_rust_entity_icp() -> None:
    text = LoadAgentSpec().load("icps/rust/ddd_clean/EntityICP")
    assert "# Role: EntityICP (Rust)" in text
    assert "pub struct" in text


def test_load_rust_strategy_icp() -> None:
    text = LoadAgentSpec().load("icps/rust/behavioral/StrategyICP")
    assert "# Role: StrategyICP (Rust)" in text
    assert "trait" in text


def test_load_rust_value_object_icp() -> None:
    text = LoadAgentSpec().load("icps/rust/ddd_clean/ValueObjectICP")
    assert "ValueObjectICP (Rust)" in text


def test_load_rust_simple_class_icp() -> None:
    text = LoadAgentSpec().load("icps/rust/ddd_clean/SimpleClassICP")
    assert "SimpleClassICP (Rust)" in text


def test_load_rust_test_architect() -> None:
    text = LoadAgentSpec().load("architects/rust/TestArchitect")
    assert "# Role: TestArchitect (Rust)" in text
    assert "#[cfg(test)]" in text
