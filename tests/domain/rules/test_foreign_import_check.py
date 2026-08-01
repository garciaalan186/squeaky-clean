"""Tests for foreign_import_check (extracted from DependencyRule)."""

import ast
from pathlib import Path

from squeaky_clean.domain.rules.foreign_import_check import (
    foreign_violations,
    polices_foreign,
)

_SRC = Path("src/domain/billing/payment.py")


def _node(code: str) -> ast.AST:
    return ast.parse(code).body[0]


def test_polices_only_pure_layer_production_source() -> None:
    assert polices_foreign("domain", _SRC)
    assert polices_foreign("application", Path("src/application/x/y.py"))
    assert not polices_foreign("infrastructure", Path("src/infrastructure/x.py"))
    assert not polices_foreign("domain", Path("tests/domain/test_payment.py"))
    assert not polices_foreign("domain", Path("src/domain/test_payment.py"))


def test_third_party_import_is_flagged_under_dependency_rule_name() -> None:
    out = foreign_violations(_node("import requests"), _SRC, "domain")
    assert len(out) == 1
    assert out[0].rule_name == "DependencyRule"
    assert "'requests'" in out[0].message


def test_stdlib_first_party_and_relative_imports_pass() -> None:
    for code in ("import json", "from src.domain.billing import money",
                 "from . import helper"):
        assert foreign_violations(_node(code), _SRC, "domain") == []
